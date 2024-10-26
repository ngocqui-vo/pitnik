from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


from .forms import UserRegisterForm, ProfileForm
from .models import Profile, User

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

@login_required
def user_profile(request):
    user = request.user
    if user is None:
        raise Http404('User does not exist')
    context = {'user': user}
    return render(request, 'account/profile.html', context=context)

