    
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.contrib.auth.models import User
from authy.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from notification.models import Notification
from post.models import Follow


@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)

    # notification
    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications


    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'directs':directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile': profile,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist, 
    }
    return render(request, 'directs/inbox.html', context)


@login_required
def Directs(request, username):
    Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)    
    
    user  = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)

     # notification
    notifications = Notification.objects.filter(user=request.user,is_seen=False).order_by('-date')
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Filter unseen notifications within the last week
    notificationslist = Notification.objects.filter(user=request.user, is_seen=True, date__gte=one_week_ago).order_by('-date')    
    unseen_count = notifications.count()  # Count unseen notifications


    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile':profile,
        'notifications': notifications,
        'unseen_count': unseen_count,
        'notificationslist':notificationslist, 
    }
    return render(request, 'directs/inbox.html', context)

def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.sender_message(from_user, to_user, body)
        return redirect('inbox')

def UserSearch(request):
    user = request.user    
    query = request.GET.get('q')
    context = {}
    messages = Message.get_message(user=request.user)
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
            'messages': messages,
            'follow_status':follow_status

            }   

    return render(request, 'directs/search.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
    return redirect('message')
