from django.contrib import admin
from .models import NotifyType, Notification

# Register your models here.
admin.site.register(NotifyType)
admin.site.register(Notification)
