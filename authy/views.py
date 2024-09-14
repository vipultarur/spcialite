from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from authy.models import Profile
from post.models import Follow, Post, Reel, Stream
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from status.models import Status  # Assuming you're using Django's built-in User model
from .forms import EditProfileForm, UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
def UserProfile(request, username):
    # Ensure the profile exists or create one for the current user
    Profile.objects.get_or_create(user=request.user)
    
    # Get the user object or return 404 if not found
    user = get_object_or_404(User, username=username)
    
    # Get the user's profile
    profile = Profile.objects.get(user=user)
    
    # Determine the URL name to decide what to display
    url_name = resolve(request.path).url_name

    # Fetch posts and reels based on the URL name
    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
        reels = Reel.objects.filter(user=user).order_by('-posted')  # Fetch user's reels
    else:
        posts = profile.favourite.all()
        reels = []  # No reels to show in this case

    # Count various statistics
    posts_count = Post.objects.filter(user=user).count()
    reel_count = Reel.objects.filter(user=user).count()

    followers = Follow.objects.filter(following=user)
    following = Follow.objects.filter(follower=user)

    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    following_users = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    statuses = Status.objects.filter(user__in=following_users).order_by('-created_at')

    user_statuses = {}
    for status in statuses:
        if status.user not in user_statuses:
            user_statuses[status.user] = []
        user_statuses[status.user].append(status)

    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()    
    # Pagination
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)
    totalpost=posts_count+reel_count
    context = {
        'posts_paginator': posts_paginator,
        'profile': profile,
        'posts': posts,
        'reels': reels,  # Add reels to the context
        'url_name': url_name,
        'favourite': profile.favourite.all(),
        'posts_count': posts_count,
        'reel_count': reel_count,
        'totalpost':totalpost,
        'following_count': following_count,
        'followers_count': followers_count,
        'follow_status': follow_status,
        'followers': followers,
        'following': following,
        'follow_status_list': {
            'following_users': following_users  # List of IDs that the request.user is following
        },
        'statuses':statuses,
        'user_statuses':user_statuses,
    }

    return render(request, 'profile.html', context)


def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:15]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))
    
def Remove_follower(request, follower_id):
    follower = get_object_or_404(User, id=follower_id)
    
    # Check if this follower is actually following the request.user
    follow_relationship = Follow.objects.filter(following=request.user, follower=follower)
    
    if follow_relationship.exists():
        # Remove the follower relationship
        follow_relationship.delete()

    # Redirect back to the profile page or wherever you'd like
    return redirect('profile', username=request.user.username)


def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            return redirect('profile', profile.user.username)
    else:
        form = EditProfileForm(instance=request.user.profile)

    context = {
        'form':form,
    }
    return render(request, 'editprofile.html', context)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # Profile.get_or_create(user=request.user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account was created!!')

            # Automatically Log In The User
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],)
            login(request, new_user)
            # return redirect('editprofile')
            return redirect('index')
            
    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'sign-up.html', context)

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'sign-in.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')