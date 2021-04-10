from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer
from django.core.serializers import serialize
from .models import Route, Airport, Nav, Chart


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ('id', 'name', 'waypoints')


class ChartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = ('id', 'typ', 'name', 'version', 'use')


class AirportSerializer(serializers.ModelSerializer):

    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    @staticmethod
    def get_type(obj):
        return 'apt'

    def get_lat(self, obj):
        return obj.fix.x

    def get_lng(self, obj):
        return obj.fix.y

    class Meta:
        model = Airport
        fields = ('icao', 'name', 'lat', 'lng', 'elevation', 'type')


class NavSerializer(serializers.ModelSerializer):

    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    def get_lat(self, obj):
        return obj.fix.x

    def get_lng(self, obj):
        return obj.fix.y

    class Meta:
        model = Nav
        fields = ('icao', 'name', 'lat', 'lng', 'elevation', 'type', 'details')
