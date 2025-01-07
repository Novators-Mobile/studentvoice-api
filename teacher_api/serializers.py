from rest_framework import serializers
from admin_api.models import Meeting


class MeetingPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['subject', 'date', 'type', 'name']