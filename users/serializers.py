from .models import CustomUser
from rest_framework import serializers


class FullAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            data=validated_data['data'],
            private=validated_data['private'],
            invoices=validated_data['invoices'],
            payments=validated_data['payments']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    groups = serializers.SerializerMethodField()

    def get_groups(self, user):
        return [g.name for g in user.groups.all()]

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'firstname',
                  'lastname', 'is_admin', 'groups', 'data', 'private', 'invoices', 'payments', 'notifications')


class BasicAccountSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    def get_groups(self, user):
        return [g.name for g in user.groups.all()]

    class Meta:
        model = CustomUser
        fields = ('id', 'firstname', 'lastname', 'groups', 'data')
