from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('user/profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('user/photos/<int:user_id>/', views.user_photos, name='user_photos'),
    path('user/notifications/<int:user_id>/', views.user_notifications, name='user_notifications'),
    path('api/posts/', views.post_list, name='post_list'),
    path('create_post_with_images/', views.PostCreateView.as_view(), name='create_post_with_images'),
    path('api/comment/add_comment/', views.add_comment, name='add_comment'),
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like_post'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('respond-to-friend-request/<int:friendship_id>/<str:action>/', views.respond_to_friend_request, name='respond_to_friend_request'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),

]

