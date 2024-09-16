from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models  # Add this import
from django.utils import timezone

from post.models import Follow
from status.models import Status
from .form import StatusForm

# Create your views here.

# Custom validator to check file type
def validate_media_file(value):
    valid_extensions = ['jpg', 'jpeg', 'png', 'mp4', 'mov']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError('File type not supported. Please upload an image or video.')

@login_required
def upload_status(request):
    if request.method == 'POST':
        form = StatusForm(request.POST, request.FILES)
        if form.is_valid():
            new_status = form.save(commit=False)
            new_status.user = request.user
            new_status.save()
            return redirect('index')  # Redirect to home page or status list
    else:
        form = StatusForm()

    return render(request, 'newstatus.html', {'form': form})


@login_required
def user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    statuses = Status.objects.filter(user=user, expires_at__gt=timezone.now()).order_by('-created_at')
    
    context = {
        'user': user,
        'statuses': statuses
    }
    return render(request, 'statusview.html', context)

@login_required
def user_status(request, user_id):
    # Get the user whose statuses you want to display
    user = get_object_or_404(User, id=user_id)

    # Check if the logged-in user is following this user
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    # If the logged-in user is following, display statuses, otherwise redirect or show message
    if is_following:
        statuses = Status.objects.filter(user=user).order_by('-created_at')
        
        # Determine media type for each status
        for status in statuses:
            if status.media.url.endswith(('.mp4', '.mov')):
                status.media_type = 'video'
            else:
                status.media_type = 'image'

        context = {
            'user': user,
            'statuses': statuses,
        }
        return render(request, 'statusview.html', context)
    
@login_required
def profile_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    statuses = Status.objects.filter(user=user).order_by('-created_at')
    for status in statuses:
        status.media_type = 'video' if status.media.url.endswith(('.mp4', '.mov')) else 'image'
    
    return render(request, 'profile_status.html', {'user': user, 'statuses': statuses})    





