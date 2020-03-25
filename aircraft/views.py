import json
import logging

from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import AircraftSerializer
from .models import Aircraft


# Create your views here.

class AircraftView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Flight Instructor').exists():
                queryset = Aircraft.objects.all()
            else:
                queryset = Aircraft.objects.filter(
                    Q(owner=request.user) | Q(public=True))
        else:
            queryset = Aircraft.objects.filter(public=True)
        serializer = AircraftSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        aircraft, created = Aircraft.objects.get_or_create(
            owner=request.user, name=request.data['name'],
            defaults={'model': request.data['model']})
        aircraft.model = request.data['model']
        aircraft.save()
        serializer = AircraftSerializer(aircraft)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        aircraft = Aircraft.objects.get(id=pk, owner=request.user)
        aircraft.delete()
        return Response()
