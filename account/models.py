from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=False, blank=False, default='default.jpg')
    background_image = models.ImageField(upload_to='backgrounds/', null=False, blank=False, default='default.jpg')
    phone = models.CharField(max_length=20, default='')
    bio = models.TextField(max_length=500, default='')
    gender = models.CharField(max_length=20, default='male',choices=[('male', 'Male'), ('female', 'Female')])

    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path)
        # Resize ảnh thành 39x39 pixel
        new_img = img.resize((39, 39))
        new_img.save(self.avatar.path)