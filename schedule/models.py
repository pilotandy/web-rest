from django.db import models
from django.contrib.postgres.fields import JSONField
from users.models import CustomUser

# Create your models here.


class Event(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    data = JSONField()
