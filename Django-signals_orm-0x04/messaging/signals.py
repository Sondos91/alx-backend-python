from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Message, Notification, MessageHistory


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal to automatically clean up all data associated with a deleted user.
    
    This signal is triggered after a User instance is deleted. It ensures that
    all related data (messages, notifications, message history) is properly cleaned up.
    Note: This is a backup cleanup mechanism. The main cleanup happens in the view.
    """
    try:
        with transaction.atomic():
            # Clean up messages sent by the deleted user
            sent_messages = Message.objects.filter(sender=instance)
            sent_count = sent_messages.count()
            sent_messages.delete()
            
            # Clean up messages received by the deleted user
            received_messages = Message.objects.filter(receiver=instance)
            received_count = received_messages.count()
            received_messages.delete()
            
            # Clean up notifications for the deleted user
            notifications = Notification.objects.filter(user=instance)
            notification_count = notifications.count()
            notifications.delete()
            
            # Clean up message history edits by the deleted user
            message_edits = MessageHistory.objects.filter(edited_by=instance)
            edit_count = message_edits.count()
            message_edits.delete()
            
            print(f"User {instance.username} deleted. Cleaned up: "
                  f"{sent_count} sent messages, {received_count} received messages, "
                  f"{notification_count} notifications, {edit_count} message edits")
                  
    except Exception as e:
        print(f"Error cleaning up data for deleted user {instance.username}: {str(e)}")


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal to log the old content of a message before it's updated.
    
    This signal is triggered before a Message instance is saved. If the message
    already exists and the content has changed, it creates a MessageHistory record.
    """
    if instance.pk:  # Only for existing messages (not new ones)
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                # Content has changed, log the old version
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content,
                    edited_by=instance.sender,  # Assuming the sender is editing
                    edited_at=timezone.now()
                )
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
                print(f"Message edit logged for message {instance.pk} by {instance.sender.username}")
        except Message.DoesNotExist:
            # This shouldn't happen, but handle it gracefully
            pass


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to automatically create a notification when a new message is created.
    
    This signal is triggered after a Message instance is saved. If it's a new message
    (created=True), it will automatically create a notification for the receiver.
    """
    if created:
        # Determine notification type based on whether it's a reply
        notification_type = 'reply' if instance.is_reply else 'message'
        
        # Create appropriate title based on message type
        if instance.is_reply:
            title = f'Reply from {instance.sender.username}'
            content = f'You received a reply: "{instance.get_short_content()}"'
        else:
            title = f'New message from {instance.sender.username}'
            content = f'You received a new message: "{instance.get_short_content()}"'
        
        # Create notification for the message receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type=notification_type,
            title=title,
            content=content
        )
        
        print(f"{notification_type.capitalize()} notification created for {instance.receiver.username} from {instance.sender.username}")


@receiver(post_save, sender=Message)
def handle_message_edit(sender, instance, created, **kwargs):
    """
    Signal to handle message edits and create edit notifications.
    """
    if not created and instance.edited:
        # Message was edited, create notification for receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='edit',
            title=f'Message edited by {instance.sender.username}',
            content=f'Message was edited: "{instance.get_short_content()}"'
        )
        
        print(f"Edit notification created for {instance.receiver.username}")


@receiver(post_save, sender=Message)
def update_message_read_status(sender, instance, **kwargs):
    """
    Signal to update notification read status when a message is marked as read.
    """
    if instance.is_read:
        # Mark related notifications as read
        Notification.objects.filter(
            user=instance.receiver,
            message=instance,
            is_read=False
        ).update(is_read=True)


def create_system_notification(user, title, content):
    """
    Utility function to create system notifications.
    
    Args:
        user: The user to notify
        title: The notification title
        content: The notification content
    """
    Notification.objects.create(
        user=user,
        notification_type='system',
        title=title,
        content=content
    ) 