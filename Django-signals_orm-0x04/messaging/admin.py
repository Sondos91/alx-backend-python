from django.contrib import admin
from django.utils.html import format_html
from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Message model.
    """
    list_display = ('sender', 'receiver', 'get_short_content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'receiver', 'content', 'timestamp')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
    )
    
    def get_short_content(self, obj):
        """Display shortened content in admin list."""
        return obj.get_short_content()
    get_short_content.short_description = 'Content'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('sender', 'receiver')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """
    list_display = ('user', 'notification_type', 'title', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at', 'user')
    search_fields = ('user__username', 'title', 'content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'message', 'notification_type', 'title', 'content')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'message')
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Admin action to mark notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """Admin action to mark notifications as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread" 