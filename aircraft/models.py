from django.db import models
from django.contrib.postgres.fields import JSONField
from users.models import CustomUser

# Create your models here.


class Aircraft(models.Model):
    name = models.CharField(max_length=10)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    model = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.owner.firstname + ' ' + self.owner.lastname + ': ' + self.name
