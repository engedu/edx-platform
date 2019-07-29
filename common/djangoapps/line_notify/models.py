from django.db import models
from django.contrib.auth.models import User


class LineToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    status = models.IntegerField()

