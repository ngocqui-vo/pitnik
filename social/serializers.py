from rest_framework import serializers
from .models import Post, ImagePost
from django.contrib.auth.models import User
from account.serializers import ProfileSerializer

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagePost
        fields = ['id', 'image']


class CreatePostSerializer(serializers.ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'images']


class UserPostSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class PostSerializer(serializers.ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)
    user = UserPostSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'images', 'user', 'created_at']