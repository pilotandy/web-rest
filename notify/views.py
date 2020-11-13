from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

from googlevoice import Voice

import json
import logging
import traceback

logger = logging.getLogger('django')


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


def SendNotification(users, subject, message):
    print(users)
    for user in users:
        n = Notification.objects.create(
            owner=user, title=subject, text=message)
        n.save()

        # Distribute
        SendEmail(user, subject, message)
        # SendSms(user, subject, message)


def SendEmail(user, subject, message):
    try:
        print(user.data['notify']['email'])
        if(user.data['notify']['email']):
            print("sending email to " + str(user))
            from_email = 'PilotAndy Aviation <automated@pilotandy.com>'
            msg = EmailMessage(subject, message, from_email, [
                str(user)], cc=['andy@pilotandy.com'])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    except:
        print("Exception: " + traceback.format_exc())
        pass


def SendSms(user, subject, message):
    if(user.data['notify']['sms']):
        text = subject + "\n" + message
        voice = Voice()
        voice.send_sms(user.data['phone'], text)
