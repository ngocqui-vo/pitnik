from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name',
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
        })

    class Meta:
        model = User
        fields = ('first_name', 'last_name','username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({
            'placeholder': 'Phone',
        })
        self.fields['gender'].initial = 'male'
        self.fields['gender'].widget = forms.Select(choices=self.fields['gender'].choices)

    class Meta:
        model = Profile
        fields = ('phone', 'gender')



