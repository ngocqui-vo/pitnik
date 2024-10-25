from django.contrib.auth import logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Post, ImagePost, Comment, Like
from .serializers import CreatePostSerializer, PostSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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