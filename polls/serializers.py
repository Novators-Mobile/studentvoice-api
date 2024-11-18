from rest_framework import serializers
from .models import PollResult, Poll


class PollSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Poll
        fields = ['id', 'subject']


class PollGetSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Poll
        fields = ['id', 'subject', 'qrcode_path', 'average_mark']


class PollResultSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PollResult
        fields = '__all__'
