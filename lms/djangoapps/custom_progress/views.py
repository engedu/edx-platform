from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.db import transaction
from django.db.models import Max
from django.http import Http404
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_control
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from courseware.masquerade import setup_masquerade
from courseware.courses import get_course_with_access, get_studio_url
from courseware.access import has_access, has_ccx_coach_role
from lms.djangoapps.ccx.custom_exception import CCXLocatorValidationException
from openedx.features.enterprise_support.api import data_sharing_consent_required
from student.models import CourseEnrollment
from util.views import ensure_valid_course_key

from lms.djangoapps.grades.models import PersistentCourseGrade


@transaction.non_atomic_requests
@login_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@ensure_valid_course_key
@data_sharing_consent_required
def show_progress(request, course_id, student_id=None):
    course_key = CourseKey.from_string(course_id)

    with modulestore().bulk_operations(course_key):
        return _show_progress(request, course_key, student_id)


def _show_progress(request, course_key, student_id):
    if student_id is not None:
        try:
            student_id = int(student_id)
        except ValueError:
            raise Http404

    course = get_course_with_access(request.user, "load", course_key)
    staff_access = bool(has_access(request.user, 'staff', course))

    masquerade = None
    if student_id is None or student_id == request.user.id:
        # This will be a no-op for non-staff users, returning request.user
        masquerade, student = setup_masquerade(request, course_key, staff_access, reset_masquerade_data=True)
    else:
        try:
            coach_access = has_ccx_coach_role(request.user, course_key)
        except CCXLocatorValidationException:
            coach_access = False

        has_access_on_students_profiles = staff_access or coach_access
        # Requesting access to a different student's profile
        if not has_access_on_students_profiles:
            raise Http404
        try:
            student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            raise Http404

    # NOTE: To make sure impersonation by instructor works, use
    # student instead of request.user in the rest of the function.

    # The pre-fetching of groups is done to make auth checks not require an
    # additional DB lookup (this kills the Progress page in particular).
    student = User.objects.prefetch_related("groups").get(id=student.id)
    if request.user.id != student.id:
        # refetch the course as the assumed student
        course = get_course_with_access(student, 'load', course_key, check_if_enrolled=True)

    # NOTE: To make sure impersonation by instructor works, use
    # student instead of request.user in the rest of the function.

    course_grade = CourseGradeFactory().read(student, course)
    # all_course_grade = CourseGradeFactory().iter()
    courseware_summary = course_grade.chapter_grades.values()

    enrolled_students = User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
    ).order_by('username')

    print("LV1")
    # for i in CourseGradeFactory().iter(enrolled_students, course_key):
    #     print(i)
    max_percent_grade = _max_grade_course(request, course, course_key)
    print("LV2")
    print('************************************************************')
    print(max_percent_grade)
    print('************************************************************')
    # studio_url = get_studio_url(course, 'settings/grading')
    # checking certificate generation configuration
    enrollment_mode, _ = CourseEnrollment.enrollment_mode_for_user(student, course_key)
    context = {
        "course": course,
        'student': student,
        'grade_summary': course_grade.summary,
        'max_percent_grade': max_percent_grade
    }
    return render_to_response("custom_progress/custom_progress.html", context)


def _max_grade_course(request, course, course_key):

    enrolled_students = User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
    ).order_by('username')

    course_grades = CourseGradeFactory().iter(enrolled_students, course=course)

    max_percent_grade = 0.0

    for course_grade in course_grades:
        if max_percent_grade < course_grade.course_grade.percent:
            max_percent_grade = course_grade.course_grade.percent

    return max_percent_grade

