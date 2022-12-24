from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class CustomUser(AbstractUser):

    username = None
    email = models.EmailField('Email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    holiday = models.CharField(max_length=100, null=True, blank=True)
    objects = UserManager()


class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    likes = models.ManyToManyField(
        CustomUser, related_name='likes', blank=True)

    def __str__(self):
        return self.text
