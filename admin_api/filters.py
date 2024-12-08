import django_filters

from .models import *


class UniversityFilter(django_filters.FilterSet):
    class Meta:
        model = University
        fields = ['name']


class MeetingFilter(django_filters.FilterSet):

    class Meta:
        model = Meeting
        fields = '__all__'


class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Subject
        fields = ['teachers']


class TeacherFilter(django_filters.FilterSet):
    class Meta:
        model = Teacher
        fields = ['university']
