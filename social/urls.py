from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('user/delete_account/', views.delete_account, name='delete_account'),
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
    path('group/list/', views.user_groups_list, name='user_groups_list'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/post/', views.GroupPostCreateView.as_view(), name='create_group_post'),
    path('group/<int:group_id>/members/', views.manage_group_member, name='manage_group_member'),
    
    path('search-users/', views.search_users, name='search_users'),

    path('group/<int:group_id>/join-request/', views.request_join_group, name='request_join_group'),
    path('group/join-request/<int:request_id>/handle/', views.handle_join_request, name='handle_join_request'),

    path('group/post/<int:post_id>/handle/', views.handle_pending_post, name='handle_pending_post'),

    path('groups/discover/', views.discover_groups, name='discover_groups'),

    path('pages/', views.page_list, name='page_list'),
    path('pages/create/', views.create_page, name='create_page'),
    path('pages/<int:page_id>/', views.page_detail, name='page_detail'),
    path('pages/<int:page_id>/update/', views.update_page, name='update_page'),
    path('pages/<int:page_id>/delete/', views.delete_page, name='delete_page'),
    path('pages/<int:page_id>/posts/create/', views.create_page_post, name='create_page_post'),
    path('pages/<int:page_id>/manage-admins/', views.manage_page_admins, name='manage_page_admins'),

    path('change-password/', views.change_password_user, name='change_password'),
]

