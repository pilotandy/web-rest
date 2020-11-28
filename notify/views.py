from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings

from .models import NotifyType, Notification
from .serializers import NotifyTypeSerializer
from .serializers import NotificationSerializer

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

from twilio.rest import Client

import json
import logging
import traceback

logger = logging.getLogger('django')


class NotifyTypeViewSet(viewsets.ModelViewSet):
    serializer_class = NotifyTypeSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = NotifyType.objects.all()


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Notification.objects.all()

    def get_queryset(self):

        # TODO: only get the last umpteen days?
        lookup = self.lookup_url_kwarg or self.lookup_field
        if lookup and lookup in self.kwargs:
            # Detail view
            query_set = Notification.objects.filter(
                owner=self.request.user, pk=self.kwargs[lookup])
            query_set.update(viewed=True)

        else:
            # List view
            query_set = Notification.objects.filter(
                owner=self.request.user).order_by('-date')

        return query_set


def SendNotification(evt_code, users, subject, message):
    for user in users:
        n = Notification.objects.create(
            owner=user, title=subject, text=message)
        n.save()

        # Distribute
        evt = user.notifications.get(evt_code, None)
        if(evt and evt['email']):
            SendEmail(user, subject, message)
        if(evt and evt['sms']):
            SendSms(user, subject, message)


def SendEmail(user, subject, message):
    try:
        from_email = 'PilotAndy Aviation <automated@pilotandy.com>'
        msg = EmailMessage(subject, message, from_email, [
            str(user)], cc=['andy@pilotandy.com'])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    except:
        print(traceback.format_exc())


def SendSms(user, subject, message):
    try:
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        msg = client.messages.create(
            to=user.data['phone'], 
            from_= settings.TWILIO_FROM,
            body=message)
    except:
        print(traceback.format_exc())

