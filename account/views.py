from django.shortcuts import render

# Create your views here.

from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from .forms import SignUpForm, UserUpdateForm, CustomerUpdateForm
from .models import Profile

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'User or password is invalid!!!')
            return redirect('user_login')
    return render(request, 'account/login.html', {})


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        forms = SignUpForm(request.POST)

        if forms.is_valid():
            # Lấy dữ liệu từ form
            first_name = forms.cleaned_data.get('first_name')
            last_name = forms.cleaned_data.get('last_name')
            email = forms.cleaned_data.get('email')
            phone = forms.cleaned_data.get('phone')
            address = forms.cleaned_data.get('address')

            user = forms.save(commit=False)
            user.is_staff = True
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            customer = Profile.objects.create(user=user, phone=phone, address=address)
            customer.save()
            
            return redirect('user_login')
        else:
            messages.error(request, 'User already exist!!!')
            return redirect('user_register')
    else:
        forms = SignUpForm()
    return render(request, 'account/register.html', {'forms': forms})


def profile(request):
    user = request.user
    if user is None:
        raise Http404('User does not exist')
    context = {'user': user}
    return render(request, 'account/profile.html', context=context)


def update_profile(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = CustomerUpdateForm(request.POST, request.FILES, instance=request.user.customer)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = CustomerUpdateForm(instance=request.user.customer)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'account/update-profile.html', context=context)
