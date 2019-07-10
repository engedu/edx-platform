from django.db import models
from opaque_keys.edx.django.models import BlockTypeKeyField, CourseKeyField, UsageKeyField
from django.contrib.auth.models import User


class Notifications(models.Model):
    xblock_id = UsageKeyField(max_length=255, db_column='module_id')
    action_method = models.IntegerField(null=True, default=None)
    due_date = models.DateTimeField(null=True, default=None)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)


class NotificationEnabled(models.Model):
    alert = models.ForeignKey(Notifications, db_index=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    is_enabled = models.IntegerField(max_length=3, default=0)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)


class NotificationToken(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    token_id = models.TextField()

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)
