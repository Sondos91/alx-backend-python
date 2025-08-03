from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    """
    def for_user(self, user):
        """
        Get all unread messages for a specific user.
        Optimized to retrieve only necessary fields.
        """
        return self.filter(
            receiver=user,
            read=False
        ).select_related('sender').only(
            'id', 'sender__id', 'sender__username', 'content', 
            'timestamp', 'read', 'parent_message'
        ).order_by('-timestamp')
    
    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        Optimized to retrieve only necessary fields using .only().
        """
        return self.filter(
            receiver=user,
            read=False
        ).select_related('sender').only(
            'id', 'sender__id', 'sender__username', 'content', 
            'timestamp', 'read', 'parent_message'
        ).order_by('-timestamp')
    
    def count_for_user(self, user):
        """
        Get the count of unread messages for a specific user.
        """
        return self.filter(
            receiver=user,
            read=False
        ).count() 