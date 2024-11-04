from django import forms
from django.contrib.auth.models import User

from account.models import Profile
from .models import Post, ImagePost
from django.forms import modelformset_factory

# Form cho Post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

# Form cho ImagePost
class ImagePostForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))  # Cho phép chọn nhiều ảnh

    class Meta:
        model = ImagePost
        fields = ['image']

# Formset cho ImagePost
ImagePostFormSet = modelformset_factory(
    ImagePost,
    form=ImagePostForm,
    extra=3  # Số lượng form cho ảnh mặc định, bạn có thể thay đổi
)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Các trường cần cập nhật


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'background_image', 'phone', 'bio', 'gender']


class UserPostSearchForm(forms.Form):
    query = forms.CharField(label='Tìm kiếm', max_length=100, required=False)
