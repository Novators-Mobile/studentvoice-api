from rest_framework import serializers
from .models import Form


class FormSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Form
        fields = ['form_url', 'form_id', "meeting"]
