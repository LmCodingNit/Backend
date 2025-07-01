from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        FOUNDER = 'FOUNDER', 'Founder'
        INVESTOR = 'INVESTOR', 'Investor'
        GOVERNMENT = 'GOVERNMENT', 'Government'
        ASPIRING = 'ASPIRING', 'Aspiring Founder'

    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.ASPIRING)
    full_name = models.CharField(max_length=255, blank=True)