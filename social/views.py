from asgiref.sync import async_to_sync
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Post, ImagePost, Comment, Like, Friendship, Notification, Message, Room, Follow, ReportPost
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import User, Profile
from channels.layers import get_channel_layer
from .forms import PostForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def index(request):
    return render(request, 'social/index.html')


class PostPagination(PageNumberPagination):
    page_size = 2  # Mỗi trang hiển thị 10 bài viết
    # page_size_query_param = 'page_size'  # Người dùng có thể điều chỉnh số bài viết trên mỗi trang
    # max_page_size = 100  # Giới hạn tối đa số bài viết mỗi trang là 100


@api_view(['GET'])
def post_list(request):
    posts = Post.objects.order_by('-created_at').filter(is_blocked=False)  # Lấy tất cả bài viết từ database
    paginator = PostPagination()  # Sử dụng class phân trang đã tạo
    result_page = paginator.paginate_queryset(posts, request)  # Phân trang kết quả

    # Lấy danh sách các bài viết mà người dùng đã "like"
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    # Tạo context chứa danh sách bài viết đã phân trang
    context = {
        'posts': result_page,  # Dữ liệu đã phân trang
        'user': request.user,
        'liked_posts_ids': liked_posts_ids,  # Thêm danh sách ID bài viết đã "like",

    }

    # Render template với context đã tạo
    rendered_html = render_to_string('ajax/get_post.html', context, request=request)

    # Trả về phản hồi với HTML
    return Response({
        'html': rendered_html,
        'pagination': {
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        }
    })


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    images = ImagePost.objects.filter(post=post)


    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()

            # Xóa ảnh nếu có yêu cầu xóa
            images_to_delete = request.POST.getlist('images_to_delete')
            if images_to_delete:
                ImagePost.objects.filter(id__in=images_to_delete).delete()

            # Thêm ảnh mới nếu có
            new_images = request.FILES.getlist('images')
            for image in new_images:
                ImagePost.objects.create(post=post, image=image)

            return redirect('index')  # Điều hướng về trang chi tiết bài đăng sau khi chỉnh sửa

    else:
        form = PostForm(instance=post)

    return render(request, 'social/edit_post.html', {'form': form, 'post': post, 'images': images})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Kiểm tra xem người dùng có quyền xóa bài đăng không
    if request.user == post.user:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this post.")

    return redirect('index')

class PostCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Để xử lý file upload

    def post(self, request, *args, **kwargs):
        content = request.data.get('content')  # Lấy nội dung bài đăng
        images = request.FILES.getlist('images')  # Lấy danh sách các file hình ảnh
        user = request.user

        # Tạo bài đăng mới
        post = Post.objects.create(user=user, content=content)

        # Lưu từng hình ảnh
        for image in images:
            ImagePost.objects.create(post=post, image=image)

        # Trả về phản hồi với thông tin bài đăng và hình ảnh đã upload
        # serializer = CreatePostSerializer(post)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

        context = {'post': post, 'images': images, 'user': user}
        rendered_html = render_to_string('ajax/created_post.html', context)

        return Response({'html': rendered_html}, status=status.HTTP_201_CREATED)


@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        post_id = request.POST.get('post_id')
        user = request.user

        # Tìm bài viết
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found.'}, status=404)

        # Tạo comment mới
        comment = Comment.objects.create(post=post, user=user, content=content)
        Notification.objects.create(
            sender=user,
            recipient=post.user,
            notification_type='commented_post',
            content=f'{request.user.username} has commented your post'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{post.user.id}",
            {
                "type": "notification_message",
                "notification": {
                    "sender": user.username,
                    "content": f"{user.username} has commented your post",
                    "avatar": f'{user.profile.avatar.url}',
                    "fullname": f'{user.first_name} {user.last_name}',
                    "is_read": False
                }
            }
        )
        # Render HTML cho comment mới
        comment_html = render_to_string('ajax/add_comment.html', {'comment': comment})

        # Trả về JSON chứa HTML của comment mới
        return JsonResponse({'comment_html': comment_html}, status=200)

    return JsonResponse({'error': 'Invalid request.'}, status=400)


class LikePostView(View):
    def post(self, request, post_id):
        if request.user.is_authenticated:
            post = Post.objects.get(id=post_id)
            # Kiểm tra xem user đã "like" post này chưa
            like, created = Like.objects.get_or_create(user=request.user, post=post)

            if created:
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.user,
                    notification_type='liked_post',
                    content=f'{request.user.username} has liked your post'
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{post.user.id}",
                    {
                        "type": "notification_message",
                        "notification": {
                            "sender": request.user.username,
                            "content": f"{request.user.username} has liked your post",
                            "avatar": f'{request.user.profile.avatar.url}',
                            "fullname": f'{request.user.first_name} {request.user.last_name}',
                            "is_read": False
                        }
                    }
                )
                # Nếu tạo mới "like", trả về thông tin thành công
                return JsonResponse({'message': 'Liked', 'liked': True, 'like_count': post.likes.count()})
            else:
                # Nếu đã "like" rồi, xóa "like" này
                like.delete()
                return JsonResponse({'message': 'Unliked', 'liked': False, 'like_count': post.likes.count()})
        return JsonResponse({'error': 'User not authenticated'}, status=403)


@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if request.user != receiver:
        friendship, created = Friendship.objects.get_or_create(
            sender=request.user,
            receiver=receiver,
            defaults={'status': 'pending'}
        )
        if created:
            Notification.objects.create(
                sender=request.user,
                recipient=receiver,
                notification_type='friend_request',
                content=f'{request.user.username} sent you a friend request'
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{receiver.id}",
                {
                    "type": "notification_message",
                    "notification": {
                        "sender": request.user.username,
                        "content": f"{request.user.username} has sent you a friend request.",
                        "avatar": f'{request.user.profile.avatar.url}',
                        "fullname": f'{request.user.first_name} {request.user.last_name}',
                        "is_read": False
                    }
                }
            )
            return JsonResponse({'status': 'success', 'message': 'Friend request sent.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Friend request already sent.'})
    return JsonResponse({'status': 'error', 'message': 'You cannot send a friend request to yourself.'})


@login_required
def respond_to_friend_request(request, sender_id, action):
    sender = get_object_or_404(User, id=sender_id)
    friendship = get_object_or_404(Friendship, sender=sender, receiver=request.user)
    notification = Notification.objects.filter(sender=sender, recipient=request.user).order_by('-created_at').first()
    # notification = get_object_or_404(Notification, sender=sender, recipient=request.user)
    notification.is_actioned = True
    notification.save()
    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        Notification.objects.create(
            sender=request.user,
            recipient=friendship.sender,
            notification_type='friend_request_accepted',
            content=f'{request.user.first_name} {request.user.last_name} accepted your friend request'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{sender.id}",
            {
                "type": "notification_message",
                "notification": {
                    "sender": request.user.username,
                    "content": f"{request.user.first_name} {request.user.last_name} has accepted your friend request.",
                    "avatar": f'{request.user.profile.avatar.url}',
                    "fullname": f'{request.user.first_name} {request.user.last_name}',
                    "is_read": False
                }
            }
        )
        return JsonResponse({'status': 'success', 'message': 'Friend request accepted.'})
    elif action == 'reject':
        friendship.status = 'rejected'
        friendship.save()
        return JsonResponse({'status': 'success', 'message': 'Friend request rejected.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid action.'})


@login_required
def friend_requests(request):
    requests = Friendship.objects.filter(receiver=request.user, status='pending')
    return JsonResponse({
        'friend_requests': [{'sender': fr.sender.username, 'id': fr.id} for fr in requests]
    })



@login_required
def room(request, username1, username2):
    # Lấy user1 và user2 dựa vào username
    user1 = get_object_or_404(User, username=username1)
    user2 = get_object_or_404(User, username=username2)

    # Sắp xếp để tránh lặp phòng, chỉ cần (user1, user2) theo thứ tự nhất định
    if user1.id > user2.id:
        user1, user2 = user2, user1

    # Tạo hoặc lấy phòng chat cho cặp user1 và user2
    room, created = Room.objects.get_or_create(user1=user1, user2=user2)

    # Lấy danh sách tin nhắn trong phòng
    messages = Message.objects.filter(room=room).order_by('timestamp')

    target_user = user1 if request.user != user1 else user2

    return render(request, 'social/chat-messenger.html', {
        'room': room,
        'messages': messages,
        'user1': user1,
        'user2': user2,
        'target_user': target_user,
    })


@login_required
def unfriend(request, user_id):
    user1 = request.user
    user2 = User.objects.get(id=user_id)
    success = Friendship.unfriend(user1, user2)
    if success:
        return redirect('friend_timeline', user_id=user1.id)
    raise Http404('Unfriend error')



class EditProfileView(LoginRequiredMixin, View):
    template_name = 'social/edit-profile.html'

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
            return redirect('user_profile', user_id=request.user.id)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)


@login_required
def user_unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    follow_instance = Follow.objects.filter(follower=request.user, following=user_to_unfollow)

    if follow_instance.exists():
        follow_instance.delete()  # Xóa record follow khỏi cơ sở dữ liệu

    return redirect('user_follow', user_id=request.user.id)



################ user

@login_required
def user_notifications(request, user_id):
    user = User.objects.get(id=user_id)
    if not request.user.is_authenticated and user != request.user:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    for notification in notifications:
        notification.is_read = True
        notification.save()

    context = {
        'notifications': notifications,
        'posts': user.posts.filter(is_blocked=False),
        'user': user,
    }
    return render(request, 'social/notifications.html', context=context)


@login_required
def friend_timeline(request, user_id):
    user = User.objects.get(id=user_id)
    friendships = Friendship.objects.filter(
        (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
    )

    # Lấy danh sách bạn bè từ các yêu cầu kết bạn này
    friends = []
    for friendship in friendships:
        if friendship.sender == user:
            friends.append(friendship.receiver)
        else:
            friends.append(friendship.sender)
    add_friend = True
    if (user == request.user
            or user.sent_friend_requests.filter(receiver=request.user).exists()
            or request.user.sent_friend_requests.filter(receiver=user).exists()
            or user.received_friend_requests.filter(receiver=request.user).exists()
            or request.user.received_friend_requests.filter(receiver=user).exists()):
        add_friend = False
    add_follow = True
    if user == request.user or Follow.objects.filter(follower=request.user, following=user).exists():
        add_follow = False
    context = {
        'friends': friends,
        'friends_count': len(friends),
        'user': user,
        'posts': user.posts.filter(is_blocked=False),
        'friend_page': True,
        'add_friend': add_friend,
        'add_follow': add_follow,
    }
    return render(request, 'social/timeline-friends2.html', context=context)

@login_required
def user_follow(request, user_id):
    user = User.objects.get(id=user_id)
    if not user:
        raise Http404('User not found')
    add_friend = True
    if (user == request.user
            or user.sent_friend_requests.filter(receiver=request.user).exists()
            or request.user.sent_friend_requests.filter(receiver=user).exists()
            or user.received_friend_requests.filter(receiver=request.user).exists()
            or request.user.received_friend_requests.filter(receiver=user).exists()):
        add_friend = False
    add_follow = True
    if user == request.user or Follow.objects.filter(follower=request.user, following=user).exists():
        add_follow = False
    context = {
        'user': user,
        'posts': user.posts.filter(is_blocked=False),
        # 'follows': user.following.all(),
        'follow_page': True,
        'add_friend': add_friend,
        'add_follow': add_follow,
    }
    return render(request, 'social/timeline-follow.html', context)


@login_required
def user_timeline(request, user_id):
    user = User.objects.get(id=user_id)
    if not user:
        raise Http404('User not found')
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    add_friend = True
    if (user == request.user
            or user.sent_friend_requests.filter(receiver=request.user).exists()
            or request.user.sent_friend_requests.filter(receiver=user).exists()
            or user.received_friend_requests.filter(receiver=request.user).exists()
            or request.user.received_friend_requests.filter(receiver=user).exists()):
        add_friend = False
    add_follow = True
    if user == request.user or Follow.objects.filter(follower=request.user, following=user).exists():
        add_follow = False
    context = {
        'user': user,
        'posts': user.posts.filter(is_blocked=False).order_by('-created_at'),
        'liked_posts_ids': liked_posts_ids,
        'timeline': True,
        'add_friend': add_friend,
        'add_follow': add_follow,
    }
    return render(request, 'social/timeline.html', context)

@login_required
def user_photos(request, user_id):
    user = User.objects.get(id=user_id)
    if user is None:
        raise Http404('User does not exist')
    posts = Post.objects.filter(user=user)
    all_images = ImagePost.objects.filter(post__in=posts).order_by('-uploaded_at')
    sort_by = request.GET.get('sort')
    if sort_by and sort_by == 'oldest':
        all_images = all_images.order_by('uploaded_at')
    add_friend = True
    if (user == request.user
            or user.sent_friend_requests.filter(receiver=request.user).exists()
            or request.user.sent_friend_requests.filter(receiver=user).exists()
            or user.received_friend_requests.filter(receiver=request.user).exists()
            or request.user.received_friend_requests.filter(receiver=user).exists()):
        add_friend = False
    add_follow = True
    if user == request.user or Follow.objects.filter(follower=request.user, following=user).exists():
        add_follow = False
    context = {'user': user, 'images': all_images, 'posts': posts, 'photos': True, 'sort_by': sort_by, 'add_friend': add_friend, 'add_follow': add_follow}
    return render(request, 'social/timeline-photos.html', context=context)


@login_required
def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    if user is None:
        raise Http404('User does not exist')
    posts = Post.objects.filter(user=user, is_blocked=False)
    all_images = ImagePost.objects.filter(post__in=posts)
    add_friend = True
    if (user == request.user
            or user.sent_friend_requests.filter(receiver=request.user).exists()
            or request.user.sent_friend_requests.filter(receiver=user).exists()
            or user.received_friend_requests.filter(receiver=request.user).exists()
            or request.user.received_friend_requests.filter(receiver=user).exists()):
        add_friend = False

    add_follow = True
    if user == request.user or Follow.objects.filter(follower=request.user, following=user).exists():
        add_follow = False
    context = {'user': user, 'images': all_images, 'posts': posts, 'profile': True, 'add_friend': add_friend, 'add_follow': add_follow}
    return render(request, 'social/timeline-about.html', context=context)


@login_required
def user_add_follow(request, user_id):
    user = User.objects.get(id=user_id)
    if user is None:
        raise Http404('User does not exist')
    Follow.objects.create(follower=request.user, following=user)
    return redirect('user_follow', user_id=user.id)


@login_required
def report_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        report = ReportPost.objects.create(post=post, user=request.user, content=request.POST['content'])
        report.save()
        return redirect('index')
    return render(request, 'social/report-post.html', {'post_id': post_id})


@login_required
def report_list(request):
    if not request.user.is_staff:
        return redirect('index')
    reports = ReportPost.objects.order_by('-created_at')
    return render(request, 'social/report-list.html', {'reports': reports})


@login_required
def detail_post_for_report(request, report_id):
    report = ReportPost.objects.get(id=report_id)
    post = report.post
    images = ImagePost.objects.filter(post=post)
    if not post:
        raise Http404('Post does not exist')
    return render(request, 'social/detail_post.html', {'post': post, 'images': images, 'report': report})


@login_required
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
