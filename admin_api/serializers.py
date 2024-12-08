from rest_framework import serializers
from .models import CustomUser, University, Subject, Meeting, Teacher
from polls.models import Poll


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'username', 'user_type']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['name']


class UniversityGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['university', 'name']


class SubjectGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'teachers', 'university', 'name']


class MeetingSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        poll = Poll.objects.create()
        return Meeting.objects.create(**validated_data, poll=poll)

    class Meta:
        model = Meeting
        fields = ['subject', 'date', 'teacher', 'type']


class MeetingGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'subject', 'date', 'poll', 'teacher', 'type']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['first_name', 'second_name', 'patronymic', 'university', 'email', 'username']


class TeacherGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'second_name', 'patronymic', 'university', 'email', 'username']


class SearchResultSerializer(serializers.Serializer):
    subjects = serializers.ListField()
    teachers = serializers.ListField()
    universities = serializers.ListField()
