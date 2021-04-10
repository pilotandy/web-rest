import json
import logging

from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .serializers import RouteSerializer, AirportSerializer, NavSerializer, ChartSerializer
from .models import Route, Airport, Nav, Chart

logger = logging.getLogger('django')


class RouteView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        queryset = Route.objects.filter(owner=request.user)
        serializer = RouteSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        route, created = Route.objects.get_or_create(
            owner=request.user, name=request.data['name'],
            defaults={'waypoints': request.data['waypoints']})
        route.waypoints = request.data['waypoints']
        route.save()
        serializer = RouteSerializer(route)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        route = Route.objects.get(id=pk, owner=request.user)
        route.delete()
        return Response()


class ChartViewSet(viewsets.ModelViewSet):
    queryset = Chart.objects.all()
    serializer_class = ChartSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class NearestView(APIView):
    authentication_classes = []

    def post(self, request, format=None):
        point = request.data
        if point['zoom'] > 11:
            point['zoom'] = 11
        if point['zoom'] < 5:
            point['zoom'] = 5
        distance = {
            5: 0.50,
            6: 0.40,
            7: 0.30,
            8: 0.20,
            9: 0.15,
            10: 0.10,
            11: 0.05,
        }
        center = Point(point['lat'], point['lng'], srid=3857)

        airports = Airport.objects.filter(fix__distance_lte=(center, distance[point['zoom']])).annotate(
            distance=Distance("fix", center)).order_by("distance")
        airport_serializer = AirportSerializer(airports, many=True)

        navs = Nav.objects.filter(fix__distance_lte=(center, distance[point['zoom']])).annotate(
            distance=Distance("fix", center)).order_by("distance")
        nav_serializer = NavSerializer(navs, many=True)

        nearest = {
            'airports': airport_serializer.data,
            'navs': nav_serializer.data,
        }
        return Response(nearest)
