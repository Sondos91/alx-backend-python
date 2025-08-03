from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Prefetch


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
    
    def count_for_user(self, user):
        """
        Get the count of unread messages for a specific user.
        """
        return self.filter(
            receiver=user,
            read=False
        ).count()


class Message(models.Model):
    """
    Message model to store messages between users with threaded conversation support.
    """
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    read = models.BooleanField(default=False)  # New field for unread messages
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Threaded conversation support
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        help_text='Parent message this is replying to'
    )
    
    # Custom managers
    objects = models.Manager()
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['timestamp']  # Changed to chronological order for threads
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['parent_message']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['receiver', 'read']),  # Index for unread queries
        ]
    
    def __str__(self):
        if self.parent_message:
            return f"Reply from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
    
    def get_short_content(self):
        """Return a shortened version of the message content."""
        return self.content[:50] + "..." if len(self.content) > 50 else self.content
    
    def mark_as_read(self):
        """Mark the message as read."""
        self.read = True
        self.is_read = True
        self.save(update_fields=['read', 'is_read'])
    
    def mark_as_unread(self):
        """Mark the message as unread."""
        self.read = False
        self.is_read = False
        self.save(update_fields=['read', 'is_read'])
    
    def mark_as_edited(self):
        """Mark the message as edited and update the edited_at timestamp."""
        self.edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['edited', 'edited_at'])
    
    @property
    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.parent_message is not None
    
    @property
    def is_thread_starter(self):
        """Check if this message starts a new thread."""
        return self.parent_message is None
    
    def get_thread_root(self):
        """Get the root message of this thread."""
        if self.is_thread_starter:
            return self
        return self.parent_message.get_thread_root()
    
    def get_reply_count(self):
        """Get the total number of replies in this thread."""
        return self.replies.count()
    
    def get_thread_depth(self):
        """Get the depth of this message in the thread."""
        depth = 0
        current = self
        while current.parent_message:
            depth += 1
            current = current.parent_message
        return depth
    
    def get_all_replies(self, include_self=False):
        """
        Get all replies in this thread using recursive query.
        Returns a queryset with all replies ordered by timestamp.
        """
        if include_self:
            return Message.objects.filter(
                Q(id=self.id) | Q(parent_message=self)
            ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')
        
        return self.replies.select_related('sender', 'receiver', 'parent_message').order_by('timestamp')
    
    def get_thread_messages(self):
        """
        Get all messages in this thread (including the root message).
        Returns a queryset with all messages ordered by timestamp.
        """
        root = self.get_thread_root()
        return Message.objects.filter(
            Q(id=root.id) | Q(parent_message=root)
        ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')
    
    @classmethod
    def get_conversation_threads(cls, user1, user2):
        """
        Get all conversation threads between two users.
        Returns a queryset with thread starter messages.
        """
        return cls.objects.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1),
            parent_message__isnull=True  # Only thread starters
        ).select_related('sender', 'receiver').prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver').order_by('timestamp')
            )
        ).order_by('-timestamp')
    
    @classmethod
    def get_user_conversations(cls, user):
        """
        Get all conversations for a user with optimized queries.
        Returns a queryset with thread starter messages.
        """
        return cls.objects.filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True  # Only thread starters
        ).select_related('sender', 'receiver').prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver').order_by('timestamp')
            )
        ).order_by('-timestamp')
    
    def can_reply(self, user):
        """Check if a user can reply to this message."""
        return user in [self.sender, self.receiver]
    
    def get_participants(self):
        """Get all participants in this thread."""
        participants = {self.sender, self.receiver}
        for reply in self.replies.all():
            participants.add(reply.sender)
            participants.add(reply.receiver)
        return participants


class MessageHistory(models.Model):
    """
    MessageHistory model to store previous versions of edited messages.
    """
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    old_content = models.TextField()
    edited_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='message_edits'
    )
    edited_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Message History'
        verbose_name_plural = 'Message History'
    
    def __str__(self):
        return f"Edit of message {self.message.id} by {self.edited_by.username} at {self.edited_at}"
    
    def get_short_old_content(self):
        """Return a shortened version of the old content."""
        return self.old_content[:50] + "..." if len(self.old_content) > 50 else self.old_content


class Notification(models.Model):
    """
    Notification model to store notifications for users.
    """
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('system', 'System Notification'),
        ('edit', 'Message Edited'),
        ('reply', 'Message Reply'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='message'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])