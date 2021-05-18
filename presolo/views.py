import json
import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.http.response import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from square.client import Client


class PreSoloView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            user = request.user
            answers = json.loads(request.body.decode('utf8'))
            presolo = user.private.get('presolo', {})
            presolo['answers'] = answers.get('answers')
            user.private['presolo'] = presolo
            user.save()
            return Response()
        except Exception as exc:
            print(traceback.format_exc())
            return Response(str(exc), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
