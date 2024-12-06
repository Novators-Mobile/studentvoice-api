from django.db import models


class Poll(models.Model):
    average_mark = models.FloatField(null=True),
    question1_avg_mark = models.FloatField(null=True)
    question2_avg_mark = models.FloatField(null=True)
    question3_avg_mark = models.FloatField(null=True)
    question4_avg_mark = models.FloatField(null=True)
    question5_avg_mark = models.FloatField(null=True)


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
