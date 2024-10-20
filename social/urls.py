from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('api/posts/', views.post_list, name='post_list'),
    path('create_post_with_images/', views.PostCreateView.as_view(), name='create_post_with_images'),
]

