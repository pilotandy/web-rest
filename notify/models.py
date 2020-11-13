from django.db import models
from users.models import CustomUser


class Notification(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
