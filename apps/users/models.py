from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at) < timedelta(minutes=15) and not self.used



