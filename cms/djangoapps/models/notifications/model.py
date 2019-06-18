from django.db import models
from django.contrib.auth.models import User

class Notifications(models.Model):

    alert_id = models.CharField(max_length=255, unique=True)
    xblock_id = models.IntegerField()
    # student = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)


class NotificationEnabled(models.Model):
    alert = models.ForeignKey(Notifications, db_index=True)