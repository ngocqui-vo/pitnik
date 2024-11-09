from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('user/timeline/<int:user_id>/', views.user_timeline, name='user_timeline'),
    path('user/add_follow/<int:user_id>/', views.user_add_follow, name='add_follow'),
    path('user/follow/<int:user_id>/', views.user_follow, name='user_follow'),
    path('user/unfollow/<int:user_id>/', views.user_unfollow, name='user_unfollow'),
    path('user/profile/edit/', views.EditProfileView.as_view(), name='edit-profile'),
    path('user/profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('user/photos/<int:user_id>/', views.user_photos, name='user_photos'),
    path('user/friend-timeline/<int:user_id>/', views.friend_timeline, name='friend_timeline'),
    path('user/unfriend/<int:user_id>/', views.unfriend, name='unfriend_user'),
    path('user/notifications/<int:user_id>/', views.user_notifications, name='user_notifications'),
    path('api/posts/', views.post_list, name='post_list'),
    path('create_post_with_images/', views.PostCreateView.as_view(), name='create_post_with_images'),
    path('api/comment/add_comment/', views.add_comment, name='add_comment'),
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like_post'),
    path('like-comment/', views.like_comment, name='like_comment'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('respond-to-friend-request/<int:sender_id>/<str:action>/', views.respond_to_friend_request, name='respond_to_friend_request'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),


    path('chat/<str:username1>/<str:username2>/', views.room, name='room'),
    path('report-post-list/', views.report_list, name='report_list'),
    path('report-post/<int:post_id>/', views.report_post, name='report_post'),
    path('report-post/detail/<int:report_id>/', views.detail_post_for_report, name='report_post_detail'),
    path('report-post/blocked/<int:report_id>/', views.resolve_the_report, name='resolve_the_report'),

    path('user/search/', views.search, name='search'),

    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/post/', views.GroupPostCreateView.as_view(), name='create_group_post'),
    path('group/<int:group_id>/members/', views.manage_group_member, name='manage_group_member'),

    path('search-users/', views.search_users, name='search_users'),

]

