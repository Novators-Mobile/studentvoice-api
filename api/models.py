from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher')
    )

    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='admin')



