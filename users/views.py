from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from .models import CustomUser
from .serializers import FullAccountSerializer, BasicAccountSerializer

import logging

logger = logging.getLogger('django')


class CreateOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        else:
            return request.user and request.user.is_authenticated


class FlightInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Flight Instructor').exists()


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.get_queryset().exclude(
        lastname="").order_by('lastname')
    serializer_class = BasicAccountSerializer
    serializer_detail_class = FullAccountSerializer
    permission_classes = [CreateOrIsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_detail_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        """
        Special case to see the user full details.
        Unless user is request.user or CFI.
        """

        lookup = self.lookup_url_kwarg or self.lookup_field
        if lookup and lookup in self.kwargs:

            # get detailed endpoint value from url e.g, "/users/2/" => 2
            user_pk = self.kwargs[lookup]
            lookup_user = CustomUser.objects.filter(pk=user_pk).first()

            # if current user is looking at the details
            if self.request.user == lookup_user:
                return self.serializer_detail_class

            return super().get_serializer_class()
        else:
            # if current user is a Flight Instructor
            if (self.request.user.groups.filter(name='Flight Instructor').exists()):
                return self.serializer_detail_class

            return super().get_serializer_class()
