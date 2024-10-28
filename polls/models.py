from django.db import models
from admin_api.models import Meeting


class Form(models.Model):
    form_url = models.CharField(max_length=256, null=False)
    form_id = models.CharField(max_length=256, null=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
