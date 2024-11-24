from django.db import models
from django.contrib.auth.models import User
from PIL import Image

from social.models import Friendship

class Profile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=False, blank=False, default='avatars/default.png')
    background_image = models.ImageField(upload_to='backgrounds/', null=False, blank=False, default='backgrounds/default.jpg')
    phone = models.CharField(max_length=20, default='')
    bio = models.TextField(max_length=500, default='')
    gender = models.CharField(max_length=20, default='male',choices=[('male', 'Male'), ('female', 'Female')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path)
        # Resize ảnh thành 39x39 pixel
        new_img = img.resize((39, 39))
        new_img.save(self.avatar.path)

class UserProxy(User):
    class Meta:
        proxy = True

    def get_friends(self):
        # Get all accepted friendships where the user is either the sender or receiver
        friendships = Friendship.objects.filter(
            models.Q(sender=self, status='accepted') | 
            models.Q(receiver=self, status='accepted')
        )
        # Extract the friend from each friendship
        friends = [f.sender if f.receiver == self else f.receiver for f in friendships]
        return friends

