from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password-reset.html'), name='forgot_password'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password-reset-done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password-reset-form.html'), name='password_reset_confirm'),
    path('password/reset/complete', auth_views.PasswordResetCompleteView.as_view(template_name='account/password-reset-complete.html'), name='password_reset_complete'),
]