from django.shortcuts import render
from .models import ImagePost, Post
from .forms import ImagePostFormSet
# Create your views here.
def index(request):
    return render(request, 'social/index.html')


from django.shortcuts import render, redirect
from .forms import PostForm, ImagePostFormSet
from django.forms import modelformset_factory
from django.contrib import messages
from django.db import transaction


def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImagePostFormSet(request.POST, request.FILES, queryset=ImagePost.objects.none())

        if post_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Lưu bài post
                    post = post_form.save(commit=False)
                    post.user = request.user  # Giả sử bạn đã có người dùng đăng nhập
                    post.save()

                    # Lưu các ảnh
                    for form in formset.cleaned_data:
                        if form:
                            image = form['image']
                            ImagePost.objects.create(post=post, image=image)

                    messages.success(request, "Bài post và hình ảnh đã được tạo thành công!")
                    return redirect('post_list')  # Điều hướng đến danh sách bài post sau khi thành công

            except Exception as e:
                messages.error(request, "Có lỗi xảy ra trong quá trình tạo bài post.")
        else:
            messages.error(request, "Đã xảy ra lỗi khi nhập dữ liệu.")
    else:
        post_form = PostForm()
        formset = ImagePostFormSet(queryset=ImagePost.objects.none())

    return render(request, 'create_post.html', {'post_form': post_form, 'formset': formset})
