from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout
from django.db import transaction
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def message_list(request):
    """Display list of conversation threads for the current user."""
    # Get all conversation threads for the user
    conversations = Message.get_user_conversations(request.user)
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/message_list.html', context)


@login_required
def conversation_thread(request, thread_id):
    """Display a specific conversation thread with all replies."""
    thread = get_object_or_404(Message, id=thread_id)
    
    # Check if user is a participant in this thread
    if request.user not in [thread.sender, thread.receiver]:
        messages.error(request, "You don't have permission to view this conversation.")
        return redirect('messaging:message_list')
    
    # Get all messages in the thread with optimized queries
    thread_messages = thread.get_thread_messages()
    
    # Mark messages as read
    unread_messages = thread_messages.filter(
        receiver=request.user,
        is_read=False
    )
    unread_messages.update(is_read=True)
    
    context = {
        'thread': thread,
        'thread_messages': thread_messages,
        'participants': thread.get_participants(),
    }
    return render(request, 'messaging/conversation_thread.html', context)


@login_required
def send_message(request):
    """Handle sending a new message or reply."""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        parent_message_id = request.POST.get('parent_message')
        
        if receiver_id and content:
            try:
                receiver = User.objects.get(id=receiver_id)
                parent_message = None
                
                # Check if this is a reply
                if parent_message_id:
                    parent_message = get_object_or_404(Message, id=parent_message_id)
                    # Verify user can reply to this message
                    if not parent_message.can_reply(request.user):
                        messages.error(request, "You cannot reply to this message.")
                        return redirect('messaging:message_list')
                
                # Create the message
                message = Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content,
                    parent_message=parent_message
                )
                
                if parent_message:
                    messages.success(request, 'Reply sent successfully!')
                    return redirect('messaging:conversation_thread', thread_id=parent_message.get_thread_root().id)
                else:
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
def reply_to_message(request, message_id):
    """Handle replying to a specific message."""
    parent_message = get_object_or_404(Message, id=message_id)
    
    # Check if user can reply to this message
    if not parent_message.can_reply(request.user):
        messages.error(request, "You cannot reply to this message.")
        return redirect('messaging:message_list')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            # Determine the receiver (the other participant in the thread)
            if request.user == parent_message.sender:
                receiver = parent_message.receiver
            else:
                receiver = parent_message.sender
            
            # Create the reply
            reply = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                parent_message=parent_message
            )
            
            messages.success(request, 'Reply sent successfully!')
            return redirect('messaging:conversation_thread', thread_id=parent_message.get_thread_root().id)
        else:
            messages.error(request, 'Please provide message content.')
    
    context = {
        'parent_message': parent_message,
        'thread_root': parent_message.get_thread_root(),
    }
    return render(request, 'messaging/reply_to_message.html', context)


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


@login_required
def delete_account_confirm(request):
    """Display confirmation page for account deletion."""
    if request.method == 'POST':
        return delete_account(request)
    
    # Get user statistics for confirmation
    sent_messages_count = Message.objects.filter(sender=request.user).count()
    received_messages_count = Message.objects.filter(receiver=request.user).count()
    notifications_count = Notification.objects.filter(user=request.user).count()
    message_edits_count = MessageHistory.objects.filter(edited_by=request.user).count()
    
    context = {
        'sent_messages_count': sent_messages_count,
        'received_messages_count': received_messages_count,
        'notifications_count': notifications_count,
        'message_edits_count': message_edits_count,
        'total_data_count': sent_messages_count + received_messages_count + notifications_count + message_edits_count,
    }
    return render(request, 'messaging/delete_account_confirm.html', context)


@login_required
@require_POST
def delete_account(request):
    """Delete the user's account and all associated data."""
    user = request.user
    username = user.username
    
    try:
        with transaction.atomic():
            # Delete all data associated with the user
            # Messages sent by the user
            sent_messages_count = Message.objects.filter(sender=user).count()
            Message.objects.filter(sender=user).delete()
            
            # Messages received by the user
            received_messages_count = Message.objects.filter(receiver=user).count()
            Message.objects.filter(receiver=user).delete()
            
            # Notifications for the user
            notifications_count = Notification.objects.filter(user=user).count()
            Notification.objects.filter(user=user).delete()
            
            # Message history edits by the user
            message_edits_count = MessageHistory.objects.filter(edited_by=user).count()
            MessageHistory.objects.filter(edited_by=user).delete()
            
            # Finally, delete the user
            user.delete()
            
            # Log out the user
            logout(request)
            
            messages.success(
                request, 
                f'Account "{username}" has been successfully deleted. '
                f'Removed: {sent_messages_count} sent messages, '
                f'{received_messages_count} received messages, '
                f'{notifications_count} notifications, '
                f'{message_edits_count} message edits.'
            )
            
            return redirect('messaging:account_deleted')
            
    except Exception as e:
        messages.error(
            request, 
            f'An error occurred while deleting your account: {str(e)}. '
            'Please try again or contact support.'
        )
        return redirect('messaging:delete_account_confirm')


def account_deleted(request):
    """Display confirmation page after account deletion."""
    return render(request, 'messaging/account_deleted.html') 