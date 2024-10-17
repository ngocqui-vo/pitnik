from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=100, required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'phone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'image']


class CustomerUpdateForm:
    pass