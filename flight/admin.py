from django.contrib import admin
from .models import Chart, Airport, Nav, Route


class ChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'use']


# Register your models here.
admin.site.register(Airport)
admin.site.register(Nav)
admin.site.register(Chart, ChartAdmin)
admin.site.register(Route)
