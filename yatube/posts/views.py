from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render


from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required


def get_page_pagination(queryset, request):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_pagination(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_page_pagination(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    template_name = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    user_posts = post_list.count()
    following = author.following.all()
    context = {
        'author': author,
        'user_posts': user_posts,
        'following': following,
    }
    context.update(get_page_pagination(author.posts.all(), request))
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'posts/post_detail.html'
    full_post = get_object_or_404(Post, id=post_id)
    count_posts = full_post.author.posts.count()
    comment_form = CommentForm(request.POST or None)
    comments = full_post.comments.all()
    context = {
        'full_post': full_post,
        'count_posts': count_posts,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, template_name, context)


@login_required
def post_create(request):
    template_name = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, template_name, {'form': form})
    form = PostForm()
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.user != post.author:
        return redirect(
            'posts:post_detail',
            post_id=post_id,
        )
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail',
            post_id=post_id,
        )
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = get_page_pagination(post_list.all(), request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follow = get_object_or_404(User, username=username)
    already_following = Follow.objects.filter(
        user=request.user,
        author=follow
    ).exists()
    if request.user != follow and not already_following:
        Follow.objects.get_or_create(user=request.user, author=follow)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(Follow, author=following, user=request.user)
    follower.delete()
    return redirect('posts:profile', username=username)
