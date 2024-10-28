from rest_framework import serializers
from .models import CustomUser, University, Subject, Meeting


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'username', 'password']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['name', 'address']


class UniversityGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'address']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['teacher', 'university', 'name']


class SubjectGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'teacher', 'university', 'name']


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['subject', 'date']


class MeetingGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'subject', 'date']
