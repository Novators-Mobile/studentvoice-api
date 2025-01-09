from django.db import models
from django.contrib.auth.models import AbstractUser
from polls.models import Poll


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher')
    )

    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='admin')
    second_name = models.CharField(max_length=30, null=False, default='Testov')
    patronymic = models.CharField(max_length=30, null=False, default='Testovich')


class University(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256, default='none')


class Teacher(CustomUser):
    university = models.ForeignKey(University, on_delete=models.CASCADE)


class Subject(models.Model):
    teachers = models.ManyToManyField(Teacher)
    lecture_teachers = models.ManyToManyField(Teacher, related_name="lecture_teachers")
    practice_teachers = models.ManyToManyField(Teacher, related_name="practice_teachers")
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class Meeting(models.Model):
    MEETING_TYPES = (
        ('lecture', 'Лекция'),
        ('practice', 'Практика')
    )
    name = models.CharField(max_length=256, null=True)
    type = models.CharField(max_length=15, choices=MEETING_TYPES, default='lecture')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateTimeField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
