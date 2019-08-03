from celery import task
from .models import CourseNotify
from lms.djangoapps.courseware.courses import get_course_by_id

@task(name='send_line_notify', bind=True, default_retry_delay=30, max_retries=2)
def send_line_notify(x):
    course_notifies = CourseNotify.objects.filter(status=1)
    unique_course_ids = course_notify_list.value('course_id').distinct()
    print(course_notifies)
    print('****************')
    print(unique_course_ids)

    for unique_course_id in unique_course_ids:
        course_detail = get_course_by_id(unique_course_id)
        print('---------------------------------------')
        print(course_detail)
