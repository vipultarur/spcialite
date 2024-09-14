from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from authy.models import Profile
from comments.forms import CommentForm, ReelCommentForm
from comments.models import  Comments, ReelComment
from notification.models import Notification
from post.forms import NewPostform, NewReelForm
from post.models import Follow, Likes, Post, Reel, ReelLikes, ReelStream, Stream, Tag
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models

from status.form import StatusForm
from status.models import Status

@login_required
def index(request): 
    user = request.user    
    posts = Stream.objects.filter(user=user)
    reelposts = ReelStream.objects.filter(user=user)
    print("Reel Posts:", reelposts)  # Debugging line
    group_ids = []
    profile = Profile.objects.get(user=user)

    # Fetch statuses for users the current user is following
    following_users = User.objects.filter(following__follower=user)
    statuses = Status.objects.filter(user__in=following_users).order_by('-created_at')

    # Group statuses by user
    user_statuses = {}
    for status in statuses:
        if status.user not in user_statuses:
            user_statuses[status.user] = []
        user_statuses[status.user].append(status)

    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    all_users = User.objects.all()
    user_follow_status = {}

    for user in all_users:
        if user != request.user:  # Ensure you're not checking the logged-in user
            follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
            user_follow_status[user] = follow_status
    notifications = Notification.objects.filter(user=request.user, is_seen=False).order_by('-date')
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()

    if request.method == "POST":
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CommentForm()

    for post in posts:
        group_ids.append(post.post_id)
    
    post_items = Post.objects.filter(id__in=group_ids).order_by('-posted')

    context = {
        'all_users': all_users,
        'user_follow_status': user_follow_status,       
        'post_items': post_items,
        'reelposts': reelposts,
        'profile': profile,
        'form': form,  
        'follow_status': follow_status,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist': notificationslist,  
        'statuses': statuses,
        'user_statuses': user_statuses,
    }

    return render(request, 'feed.html', context)


@login_required
def reel_feed(request):
    # Fetch unseen notifications for the user
    notifications = Notification.objects.filter(user=request.user, is_seen=False).order_by('-date')

    # Fetch notifications seen within the last week
    one_week_ago = timezone.now() - timedelta(days=7)
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')
    unseen_count = notifications.count()  # Count unseen notifications

    # Fetch the user's reel stream
    user = request.user
    reels = ReelStream.objects.filter(user=user).order_by('-date')
    reel_ids = [reel.reel.id for reel in reels]
    reel_items = Reel.objects.filter(id__in=reel_ids).order_by('-posted')

    context = {
        'reel_items': reel_items,  # Pass the filtered reels to the template
        'notificationslist':notificationslist,
        'unseen_count':unseen_count,
    }
    return render(request, 'reels.html', context)


@login_required
def NewPost(request):
    user = request.user
    tags_obj = []
    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications
    unseen_count = notifications.count()  # Count unseen notifications

    
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(',')) if tag_form else []

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag.strip())
                tags_obj.append(t)
            
            # Creating a new Post object and saving it
            p = Post.objects.create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('index')  # Redirecting to the feed after post creation
    else:
        form = NewPostform()

    context = {
        'form': form,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist

    }
    return render(request, 'newpost.html', context)

@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    liked = Likes.objects.filter(user=user, post=post).exists()

    # Fetch all comments related to the post
    comments = Comments.objects.filter(post=post).order_by("-date")
    
    # notification
    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications

    
    # Handle comment form submission
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('postdetail', args=[post.id]))
    else:
        form = CommentForm()

    context = {
        'post': post,
        'liked': liked,
        'form': form,
        'comments': comments,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist
    }

    return render(request, 'postdetail.html', context)


@login_required
def delete_post(request, post_id):
    
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == "POST":
        post.delete()
        return redirect('index')  
    return render(request, 'postdetail.html', {'post': post})

@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        caption = request.POST.get('caption')
        tags_input = request.POST.get('tags')

        # Process tags
        tag_names = [tag.strip() for tag in tags_input.split(',')]
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(title=name)  # Use 'title' instead of 'name'
            tags.append(tag)

        post.caption = caption
        post.save()

        # Update many-to-many relationship
        post.tags.set(tags)
        post.save()

        return redirect('postdetail', post_id=post.id)
    else:
        form = NewPostform(instance=post)

    return render(request, 'updatepost.html', {'form': form, 'post': post})


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    return HttpResponseRedirect(reverse('postdetail', args=[post_id]))

@login_required
def Favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)
    
    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('postdetail', args=[post_id]))

@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')
    posts_count = Post.objects.filter(tags=tag).order_by('-posted').count()

    context = {
        'posts': posts,
        'tag': tag,
        'posts_count':posts_count

    }
    return render(request, 'tags.html', context)


def search(request):
    query = request.GET.get('q')  # Get the search query from the request
    user_results = []
    post_results = []

    if query:
        # Search for users (by username or any other relevant fields)
        user_results = User.objects.filter(Q(username__icontains=query))

        # Search for posts (by caption or any other relevant fields)
        post_results = Post.objects.filter(Q(caption__icontains=query))

    context = {
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
    }

    return render(request, 'search.html', context)

def messages(request):
    # notification
    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications

    context={
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist
    }
    return render(request,'messages.html')


def mark_notification_as_seen(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_seen = True
    notification.save()

    # Redirect based on the notification type
    if notification.notification_types == 1 or notification.notification_types == 2:
        return redirect('postdetail', post_id=notification.post.id)
    elif notification.notification_types == 3:
        return redirect('profile', username=notification.sender.username)
    elif notification.notification_types == 4:
        return redirect('reeldetail', id=notification.reel.id)  # Add redirection for reels

    # Fallback redirect if no matching notification type is found
    return redirect('notifications')

@login_required
def Newreel(request):

    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications


    if request.method == "POST":
        form = NewReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.user = request.user
            reel.save()
            form.save_m2m()
            return redirect('reel_feed')  # Redirect to the reel feed
    else:
        form = NewReelForm()

    return render(request, 'upload_reel.html', {'form': form})


@login_required
def reeldetail(request, id):

    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications

    reel = get_object_or_404(Reel, id=id)
    user = request.user
    comments = ReelComment.objects.filter(reel=reel).order_by('-date')
    comments_count = ReelComment.objects.filter(reel=reel).count()

    if request.method == "POST":
        form = ReelCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.reel = reel
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('reeldetail', args=[reel.id]))
    else:
        form = ReelCommentForm()

    context = {
        'reel': reel,
        'comments': comments,
        'form': form,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist,
        'comments_count':comments_count,
                
    }

    return render(request, 'reel_detail.html', context)

@login_required
def reel_like(request, id):
    user = request.user
    reel = Reel.objects.get(id=id)
    
    # Ensure you are accessing the actual value of reel.likes
    current_likes = reel.likes or 0  # Initialize with 0 if likes is None
    
    # Check if the user already liked the reel
    liked = ReelLikes.objects.filter(user=user, reel=reel).count()

    if not liked:
        # Create a new like
        ReelLikes.objects.create(user=user, reel=reel)
        current_likes += 1  # Increment the like count
    else:
        # Remove the existing like
        ReelLikes.objects.filter(user=user, reel=reel).delete()
        current_likes -= 1  # Decrement the like count

    # Update the likes field
    reel.likes = current_likes
    reel.save()

    return HttpResponseRedirect(reverse('reeldetail', args=[id]))

