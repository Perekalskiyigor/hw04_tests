from django.core.paginator import Paginator
from django.shortcuts import (
    get_object_or_404, redirect, render,
)
from .models import Group, Post, User
from .forms import PostForm
PAGINATOR_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'post_list': post_list,
        'page_obj': page_obj,

    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count = posts.count()
    context = {
        'author': author,
        'post_count': post_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'count': count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_edit = True
    form = PostForm(
        request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', pk=post.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)

    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)
