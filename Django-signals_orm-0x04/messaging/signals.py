from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to automatically create a notification when a new message is created.
    
    This signal is triggered after a Message instance is saved. If it's a new message
    (created=True), it will automatically create a notification for the receiver.
    """
    if created:
        # Create notification for the message receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message',
            title=f'New message from {instance.sender.username}',
            content=f'You received a new message: "{instance.get_short_content()}"'
        )
        
        print(f"Notification created for {instance.receiver.username} from {instance.sender.username}")


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