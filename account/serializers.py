from rest_framework import serializers
from django.contrib.auth.models import User

from account.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'