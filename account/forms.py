# social/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # Các trường cần cập nhật

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'background_image', 'phone', 'bio', 'gender']
        
class UserPostSearchForm(forms.Form):
    query = forms.CharField(label='Tìm kiếm', max_length=100, required=False)
