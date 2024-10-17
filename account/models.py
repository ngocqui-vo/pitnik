from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=False, blank=False, default='default.jpg')
    background_image = models.ImageField(upload_to='backgrounds/', null=False, blank=False, default='default.jpg')
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True, choices=[('male', 'Male'), ('female', 'Female')])

    def __str__(self) -> str:
        return self.user.username

