from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from users.models import CustomUser

# Create your models here.


class Route(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    waypoints = JSONField()

    def __str__(self):
        return self.owner.firstname + ' ' + self.owner.lastname + ': ' + self.name


class Cycle(models.Model):
    name = models.CharField(max_length=10)
    cycle = models.DateField()


class Chart(models.Model):
    typ = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    version = models.IntegerField()
    use = models.BooleanField()

    def __str__(self):
        return self.name


class Airport(models.Model):
    icao = models.CharField(max_length=5)
    name = models.CharField(max_length=50, blank=True, null=True)
    fix = models.PointField(srid=3857, null=True)
    elevation = models.FloatField(null=True)

    class Meta:
        app_label = 'flight'

    def __str__(self):
        return self.icao


class Nav(models.Model):
    icao = models.CharField(max_length=4)
    name = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    fix = models.PointField(srid=3857, null=True)
    elevation = models.FloatField(null=True)
    details = JSONField(default=dict)

    class Meta:
        app_label = 'flight'

    def __str__(self):
        return self.icao
