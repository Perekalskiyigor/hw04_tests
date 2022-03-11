
# from django.core.paginator import Paginator
from django.shortcuts import (
    get_object_or_404, redirect, render,
)
from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .utils import get_page_paginator

PAGINATOR_PAGE = 10


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('group').all()
    page_obj = get_page_paginator(request, posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    post_list = Post.objects.all()
    posts = group.posts.all()
    page_obj = get_page_paginator(request, posts)

    context = {
        'title': title,
        'group': group,
        'post_list': post_list,
        'page_obj': page_obj,

    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'group', 'author'
    ).filter(
        author=author
    )
    page_obj = get_page_paginator(request, posts)
    full_name = author.get_full_name()
    title = f'Профайл пользователя {full_name}'
    following = request.user.is_authenticated
    post_count = posts.count()
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'title': title,
        'post_count': post_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, pk):
    template = 'posts/create_post.html'
    edit_post = get_object_or_404(Post, id=pk)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Мои подписки'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_paginator(request, posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    return redirect('posts:profile', username)
