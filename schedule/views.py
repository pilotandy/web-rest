from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer
from django.db.models import Q
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.contrib.auth import get_user_model
from notify.views import SendNotification

import json
import pytz
import logging

logger = logging.getLogger('django')


def convert_to_localtime(utctime):
    utctime = parse_datetime(utctime).astimezone(timezone.utc)
    fmt = '%A %B %d, %Y at %l:%M %p %Z'
    utc = utctime.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(pytz.timezone('US/Central'))
    return localtz.strftime(fmt)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Event.objects.all()

    def get_queryset(self):
        if self.request.method == 'GET':
            now = timezone.now().isoformat()
            start = parse_datetime(
                self.request.query_params.get('start', now))
            end = parse_datetime(
                self.request.query_params.get('end', now))

            query_set = Event.objects.filter(
                Q(end__lte=end) & Q(end__gt=start) |
                Q(start__lt=end) & Q(start__gte=start) |
                Q(start__lte=start) & Q(end__gte=end))
            return query_set
        else:
            return Event.objects.all()

    @action(detail=False, methods=['post'])
    def validate(self, request, pk=None):
        evt = json.loads(request.body.decode('utf8'))
        start = parse_datetime(evt['start'])
        end = parse_datetime(evt['end'])

        query_set = Event.objects.filter(
            Q(end__lte=end) & Q(end__gt=start) |
            Q(start__lt=end) & Q(start__gte=start) |
            Q(start__lte=start) & Q(end__gte=end))

        result = True
        for q in query_set:
            if q.id != evt['id']:
                for r in q.data['resources']:
                    for ids in evt['resourceIds']:
                        if ids == r:
                            result = False

        return Response(result)

    def create(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            start = convert_to_localtime(serializer.data['start'])
            event_type = ''
            users = [get_user_model().objects.get(pk=serializer.data['owner'])]
            for r in serializer.data['data']['resources']:
                if r > 1000:
                    event_type = ' flight' + event_type
                else:
                    event_type = event_type + ' lesson'
                    cfi = get_user_model().objects.get(pk=r)
                    users.append(cfi)

            message = f"You have a{event_type} on " + start
            SendNotification(
                users, 'New Scheduled Event', message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
