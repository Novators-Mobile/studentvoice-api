from rest_framework import serializers
from admin_api.models import Meeting
from polls.models import PollResult

class MeetingPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['subject', 'date', 'type', 'name']


class PollParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollResult
        fields = ['student_first_name', 'student_second_name', 'student_patronymic']