from django.db import models
from admin_api.models import Subject


class Poll(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    qrcode_path = models.CharField(max_length=256)
    average_mark = models.FloatField(default=0)


class PollResult(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    student_first_name = models.CharField(max_length=256)
    student_second_name = models.CharField(max_length=256)
    student_patronymic = models.CharField(max_length=256)
    question1 = models.IntegerField(null=False, default=5)
    question2 = models.IntegerField(null=False, default=5)
    question3 = models.IntegerField(null=False, default=5)
    question4 = models.IntegerField(null=False, default=5)
    question5 = models.IntegerField(null=False, default=5)
    comment1 = models.CharField(max_length=1024, null=True)
    comment2 = models.CharField(max_length=1024, null=True)
