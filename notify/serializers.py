from rest_framework import serializers
from .models import NotifyType, Notification


class NotifyTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotifyType
        fields = ('sid', 'title', 'description')


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('id', 'title', 'owner', 'text', 'date', 'viewed')
