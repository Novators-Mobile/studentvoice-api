from rest_framework import serializers
from .models import CustomUser, University


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'username', 'password']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['name', 'address']


