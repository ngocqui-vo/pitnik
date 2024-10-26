from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('user/profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('user/photos/<int:user_id>/', views.user_photos, name='user_photos'),
    path('api/posts/', views.post_list, name='post_list'),
    path('create_post_with_images/', views.PostCreateView.as_view(), name='create_post_with_images'),
    path('api/comment/add_comment/', views.add_comment, name='add_comment'),
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like_post'),
]

