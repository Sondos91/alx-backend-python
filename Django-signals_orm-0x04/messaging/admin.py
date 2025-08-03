from django.contrib import admin
from django.utils.html import format_html
from .models import Message, Notification, MessageHistory


class MessageReplyInline(admin.TabularInline):
    """
    Inline admin for Message replies to show thread structure.
    """
    model = Message
    extra = 0
    readonly_fields = ('sender', 'receiver', 'timestamp', 'content', 'is_read', 'edited')
    fields = ('sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited')
    fk_name = 'parent_message'
    
    def has_add_permission(self, request, obj=None):
        """Disable adding new replies manually."""
        return False


class MessageHistoryInline(admin.TabularInline):
    """
    Inline admin for MessageHistory to show edit history within Message admin.
    """
    model = MessageHistory
    extra = 0
    readonly_fields = ('edited_at', 'edited_by', 'get_short_old_content')
    fields = ('edited_at', 'edited_by', 'get_short_old_content')
    
    def get_short_old_content(self, obj):
        """Display shortened old content."""
        return obj.get_short_old_content()
    get_short_old_content.short_description = 'Old Content'
    
    def has_add_permission(self, request, obj=None):
        """Disable adding new history records manually."""
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Message model.
    """
    list_display = ('sender', 'receiver', 'get_short_content', 'timestamp', 'is_read', 'read', 'edited', 'is_reply', 'parent_message')
    list_filter = ('is_read', 'read', 'edited', 'timestamp', 'sender', 'receiver', 'parent_message')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('timestamp', 'edited_at')
    date_hierarchy = 'timestamp'
    inlines = [MessageReplyInline, MessageHistoryInline]
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'receiver', 'content', 'timestamp', 'parent_message')
        }),
        ('Status', {
            'fields': ('is_read', 'read', 'edited', 'edited_at')
        }),
    )
    
    def get_short_content(self, obj):
        """Display shortened content in admin list."""
        content = obj.get_short_content()
        if obj.edited:
            content += " (edited)"
        if obj.is_reply:
            content += " (reply)"
        if not obj.read:
            content += " [UNREAD]"
        return content
    get_short_content.short_description = 'Content'
    
    def is_reply(self, obj):
        """Display if message is a reply."""
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Reply'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('sender', 'receiver', 'parent_message')
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_edited', 'mark_as_read_new', 'mark_as_unread_new']
    
    def mark_as_read(self, request, queryset):
        """Admin action to mark messages as read (legacy is_read field)."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read (is_read).')
    mark_as_read.short_description = "Mark selected messages as read (is_read)"
    
    def mark_as_unread(self, request, queryset):
        """Admin action to mark messages as unread (legacy is_read field)."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread (is_read).')
    mark_as_unread.short_description = "Mark selected messages as unread (is_read)"
    
    def mark_as_read_new(self, request, queryset):
        """Admin action to mark messages as read (new read field)."""
        updated = queryset.update(read=True, is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read_new.short_description = "Mark selected messages as read"
    
    def mark_as_unread_new(self, request, queryset):
        """Admin action to mark messages as unread (new read field)."""
        updated = queryset.update(read=False, is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread_new.short_description = "Mark selected messages as unread"
    
    def mark_as_edited(self, request, queryset):
        """Admin action to mark messages as edited."""
        for message in queryset:
            message.mark_as_edited()
        self.message_user(request, f'{queryset.count()} message(s) marked as edited.')
    mark_as_edited.short_description = "Mark selected messages as edited"


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the MessageHistory model.
    """
    list_display = ('message', 'edited_by', 'get_short_old_content', 'edited_at')
    list_filter = ('edited_at', 'edited_by')
    search_fields = ('message__content', 'old_content', 'edited_by__username')
    readonly_fields = ('edited_at',)
    date_hierarchy = 'edited_at'
    
    fieldsets = (
        ('Edit Details', {
            'fields': ('message', 'edited_by', 'old_content', 'edited_at')
        }),
    )
    
    def get_short_old_content(self, obj):
        """Display shortened old content in admin list."""
        return obj.get_short_old_content()
    get_short_old_content.short_description = 'Old Content'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('message', 'edited_by')


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