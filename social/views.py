from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Post, ImagePost
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
    posts = Post.objects.all()  # Lấy tất cả bài viết từ database
    paginator = PostPagination()  # Sử dụng class phân trang đã tạo
    result_page = paginator.paginate_queryset(posts, request)  # Phân trang kết quả
    serializer = PostSerializer(result_page, many=True)  # Chuyển dữ liệu thành JSON
    return paginator.get_paginated_response(serializer.data)  # Trả về dữ liệu phân trang



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
        serializer = CreatePostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
