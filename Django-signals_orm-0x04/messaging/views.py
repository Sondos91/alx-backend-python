from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Message, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def message_list(request):
    """Display list of messages for the current user."""
    # Get messages where user is either sender or receiver
    sent_messages = Message.objects.filter(sender=request.user).select_related('receiver')
    received_messages = Message.objects.filter(receiver=request.user).select_related('sender')
    
    context = {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    return render(request, 'messaging/message_list.html', context)


@login_required
def send_message(request):
    """Handle sending a new message."""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        
        if receiver_id and content:
            try:
                receiver = User.objects.get(id=receiver_id)
                message = Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content
                )
                messages.success(request, 'Message sent successfully!')
                return redirect('messaging:message_list')
            except User.DoesNotExist:
                messages.error(request, 'Invalid receiver selected.')
        else:
            messages.error(request, 'Please provide both receiver and message content.')
    
    # Get list of users for the form
    users = User.objects.exclude(id=request.user.id)
    context = {
        'users': users,
    }
    return render(request, 'messaging/send_message.html', context)


@login_required
def notification_list(request):
    """Display list of notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user).select_related('message')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'messaging/notification_list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}) 