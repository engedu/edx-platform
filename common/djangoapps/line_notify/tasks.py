from celery import task
from .models import CourseNotify, LineToken
from lms.djangoapps.courseware.courses import get_course_by_id, get_course_info_section_module
import time
import datetime
import pytz
import requests
from xmodule.modulestore.django import modulestore
from lms.djangoapps.course_api.blocks.api import get_blocks
from lms.djangoapps.course_api.blocks.forms import BlockListGetForm
from lms.djangoapps.course_api.blocks.transformers import SUPPORTED_FIELDS
import lms.djangoapps.course_blocks.api as course_blocks_api
from openedx.core.djangoapps.content.block_structure.transformers import BlockStructureTransformers
from opaque_keys.edx.keys import CourseKey
from django.contrib.auth.models import User


@task(name='send_line_notify', bind=True, default_retry_delay=30, max_retries=2)
def send_line_notify(x):
    course_notifies = CourseNotify.objects.filter(status=1, is_notified=0)
    unique_course_ids = course_notifies.values('course_id').distinct()
    course_id_pending = []

    for unique_course_id in unique_course_ids:
        course_detail = get_course_by_id(unique_course_id['course_id'])
        course_usage_key = modulestore().make_course_usage_key(unique_course_id['course_id'])
        transformers = BlockStructureTransformers()
        blocks = course_blocks_api.get_course_blocks(None, course_usage_key, transformers) 
        requested_fields = ['due'] 
        for supported_field in SUPPORTED_FIELDS:
            if supported_field.requested_field_name in requested_fields:
                for block in blocks:
                    value = blocks.get_xblock_field(block, supported_field.block_field_name)
                    if value is not None:
                        print(value - pytz.utc.localize(datetime.datetime.utcnow()))
                        # value = datetime.strptime(value)
                        timediff = value - pytz.utc.localize(datetime.datetime.utcnow())
                        if timediff < datetime.timedelta(days=7) and timediff > datetime.timedelta(days=0):
                            course_id_pending.append({
                                'course_id': unique_course_id['course_id'],
                                'time' : value
                            })
                        break
    for pending in course_id_pending:
        courses = course_notifies.filter(course_id=pending['course_id'], is_notified=0)
     
        for course in courses:
            access_token = course.line_token.token
            print(access_token)            
            course.is_notified = 1
            course.usage = course.usage + 1
            course.save()

            headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + access_token}
            res = requests.post('https://notify-api.line.me/api/notify', data={
                'message': 'Alert from ' + str(pending['course_id']) + '\nDue Date at ' + str(pending['time'])
            }, headers=headers).json()
            time.sleep(1)


@task(name='reset_notified', bind=True, default_retry_delay=30, max_retries=2)
def reset_notified(x):
    course_notifies = CourseNotify.objects.all().update(is_notified=0)
