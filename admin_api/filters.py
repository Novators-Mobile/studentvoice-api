import django_filters

from .models import *


class UniversityFilter(django_filters.FilterSet):
    class Meta:
        model = University
        fields = ['name', 'address']


class MeetingFilter(django_filters.FilterSet):
    class Meta:
        model = Meeting
        fields = ['subject', 'date']


class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Meeting
        fields = '__all__'


class TeacherFilter(django_filters.FilterSet):
    class Meta:
        model = Teacher
        fields = ['university']
