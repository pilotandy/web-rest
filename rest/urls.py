"""rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import UserViewSet
from aircraft.views import AircraftView
from schedule.views import EventViewSet
# from flight.views import NearestView, RouteView, ChartViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'event', EventViewSet)
# router.register(r'flight/chart', ChartViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    # Aircraft
    path('api/aircraft/', AircraftView.as_view()),

    # # Flight
    # path('api/flight/route/', RouteView.as_view()),
    # path('api/flight/route/<pk>/', RouteView.as_view()),
    # path('api/flight/nearest/', NearestView.as_view()),

    path('admin/', admin.site.urls),
    path('jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
