from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher')
    )

    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='admin')


class University(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)


class Subject(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class Meeting(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateTimeField()

