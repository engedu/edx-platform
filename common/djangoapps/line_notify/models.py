from django.db import models
from django.contrib.auth.models import User
from opaque_keys.edx.django.models import CourseKeyField


class LineToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    status = models.IntegerField(default=0)
    state = models.UUIDField(unique=True, null=True)


class CourseNotify(models.Model):
    line_token = models.ForeignKey(LineToken, on_delete=models.CASCADE)
    course_id = CourseKeyField(max_length=255, db_index=True)
    status = models.IntegerField()

