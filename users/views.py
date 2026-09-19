from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from blog.models import Post, Comment

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Register Successful!')
            return redirect('blog:all_posts')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('blog:all_posts_list')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile_edit(request):
    if not hasattr(request.user, 'profile'):
        from .models import Profile
        Profile.objects.create(user=request.user)
    profile = request.user.profile

    if request.method == 'POST':
        if 'avatar' in request.FILES and not profile.can_change_avatar():
            remaining = profile.get_avatar_change_remaining_days()
            messages.error(request, f'You can change your avatar only once every 3 days. Please wait {remaining} more days.')
            return redirect('users:profile_edit')

        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if 'avatar' in request.FILES:
                profile.last_avatar_change = timezone.now()
            form.save()
            messages.success(request, 'Your profile picture has been updated.')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)

    remaining = profile.get_avatar_change_remaining_days()
    return render(request, 'users/profile_edit.html', {'form': form, 'remaining_days': remaining})

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

def profile(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user
    user_posts = Post.objects.filter(author=user).order_by('-publish')
    user_comments = Comment.objects.filter(name=user.username).order_by('-created')
    return render(request, 'users/profile.html', {'user': user, 'posts': user_posts, 'comments': user_comments})

@login_required
def account_delete(request):
    if request.method == 'POST' and request.POST.get('confirm_delete'):
        username = request.user.username
        request.user.delete()
        messages.success(request, f'Account "{username}" has been permanently deleted.')
        return redirect('blog:all_posts_list')
    return render(request, 'users/account_delete.html')

@login_required
def username_change(request):
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        if new_username:
            if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                messages.error(request, 'Username already exists.')
                return redirect('users:username_change')
            request.user.username = new_username
            request.user.save()
            messages.success(request, f'User "{new_username}" has been changed.')
            return redirect('users:profile')
    form = UserChangeForm(instance=request.user)
    for field in form.fields:
        if field != 'username':
            form.fields[field].widget = forms.HiddenInput()
    return render(request, 'users/username_change.html', {'form': form})