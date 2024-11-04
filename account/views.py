from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserUpdateForm, ProfileUpdateForm
from django.views import View
from .models import Profile, User
from django.db.models import Q
from social.models import Post

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')

    return render(request, 'account/login.html')


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')

        new_user = User.objects.create(first_name=first_name, last_name=last_name, username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        Profile.objects.create(user=new_user, gender=gender, phone=phone).save()
        return redirect('index')
    return render(request, 'account/register.html')


class UserProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'social/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')  # Lấy user_id từ URL
        profile = get_object_or_404(Profile, user__id=user_id)  # Lấy profile dựa trên user_id
        context['profile'] = profile
        return context




class EditProfileView(LoginRequiredMixin, View):
    template_name = 'partial/edit-profile.html'
    
    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Chuyển hướng đến trang profile của người dùng
            return redirect('user-profile', user_id=request.user.id)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:  # Nếu query rỗng
        return render(request, 'social/search-result.html', {'users': [], 'posts': [], 'query': query})

    # User search: first_name, last_name, and full name matches
    users = Profile.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__first_name__icontains=query.split()[0]) & 
        Q(user__last_name__icontains=query.split()[-1]) |
        Q(user__first_name__icontains=query) & Q(user__last_name__icontains=query)
    )
    
    # Post search based on content
    posts = Post.objects.filter(content__icontains=query)

    # Render results to the template
    return render(request, 'social/search-result.html', {
        'users': users,
        'posts': posts,
        'query': query
    })