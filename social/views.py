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
from .models import Post, ImagePost, Comment, Like, Friendship, Notification
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import User


@login_required
def index(request):
    return render(request, 'social/index.html')


class PostPagination(PageNumberPagination):
    page_size = 2  # Mỗi trang hiển thị 10 bài viết
    # page_size_query_param = 'page_size'  # Người dùng có thể điều chỉnh số bài viết trên mỗi trang
    # max_page_size = 100  # Giới hạn tối đa số bài viết mỗi trang là 100


@api_view(['GET'])
def post_list(request):
    posts = Post.objects.order_by('-created_at')  # Lấy tất cả bài viết từ database
    paginator = PostPagination()  # Sử dụng class phân trang đã tạo
    result_page = paginator.paginate_queryset(posts, request)  # Phân trang kết quả

    # Lấy danh sách các bài viết mà người dùng đã "like"
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    # Tạo context chứa danh sách bài viết đã phân trang
    context = {
        'posts': result_page,  # Dữ liệu đã phân trang
        'user': request.user,
        'liked_posts_ids': liked_posts_ids,  # Thêm danh sách ID bài viết đã "like"
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
                # Nếu tạo mới "like", trả về thông tin thành công
                return JsonResponse({'message': 'Liked', 'liked': True, 'like_count': post.likes.count()})
            else:
                # Nếu đã "like" rồi, xóa "like" này
                like.delete()
                return JsonResponse({'message': 'Unliked', 'liked': False, 'like_count': post.likes.count()})
        return JsonResponse({'error': 'User not authenticated'}, status=403)


@login_required
def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    if user is None:
        raise Http404('User does not exist')
    posts = Post.objects.filter(user=user)
    all_images = ImagePost.objects.filter(post__in=posts)
    context = {'user': user, 'images': all_images, 'posts': posts, 'profile': True}
    return render(request, 'social/about.html', context=context)


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
    context = {'user': user, 'images': all_images, 'posts': posts, 'photos': True, 'sort_by': sort_by}
    return render(request, 'social/timeline-photos.html', context=context)


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
                recipient=receiver,
                notification_type='friend_request',
                content=f'{request.user.username} sent you a friend request'
            )
            return JsonResponse({'status': 'success', 'message': 'Friend request sent.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Friend request already sent.'})
    return JsonResponse({'status': 'error', 'message': 'You cannot send a friend request to yourself.'})


@login_required
def respond_to_friend_request(request, friendship_id, action):
    friendship = get_object_or_404(Friendship, id=friendship_id, receiver=request.user)
    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        Notification.objects.create(
            recipient=friendship.sender,
            notification_type='friend_request',
            content=f'{request.user.username} accepted your friend request'
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
def user_notifications(request, user_id):
    user = User.objects.get(id=user_id)
    if not request.user.is_authenticated and user != request.user:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'social/notifications.html', context={'notifications': notifications, 'posts': user.posts.all()})


