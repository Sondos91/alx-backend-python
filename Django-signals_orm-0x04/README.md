# Django Messaging System with Automatic Notifications

This project implements a messaging system using Django with automatic notifications triggered by Django signals. When a user receives a new message, a notification is automatically created for them.

## Features

- **Message Model**: Stores messages between users with sender, receiver, content, and timestamp
- **Notification Model**: Stores notifications linked to users and messages
- **Django Signals**: Automatically creates notifications when new messages are sent
- **Admin Interface**: Full Django admin integration for managing messages and notifications
- **Comprehensive Tests**: Unit tests covering models, signals, and integration scenarios

## Project Structure

```
Django-signals_orm-0x04/
├── manage.py
├── requirements.txt
├── README.md
├── messaging_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── messaging/
    ├── __init__.py
    ├── models.py
    ├── signals.py
    ├── apps.py
    ├── admin.py
    ├── tests.py
    ├── views.py
    └── urls.py
```

## Models

### Message Model
- `sender`: ForeignKey to User (who sent the message)
- `receiver`: ForeignKey to User (who receives the message)
- `content`: TextField (message content)
- `timestamp`: DateTimeField (when message was sent)
- `is_read`: BooleanField (whether message has been read)
- `edited`: BooleanField (whether message has been edited)
- `edited_at`: DateTimeField (when message was last edited)

### MessageHistory Model
- `message`: ForeignKey to Message (the message being edited)
- `old_content`: TextField (previous version of the message content)
- `edited_by`: ForeignKey to User (who made the edit)
- `edited_at`: DateTimeField (when the edit was made)

### Notification Model
- `user`: ForeignKey to User (who gets the notification)
- `message`: ForeignKey to Message (optional link to related message)
- `notification_type`: CharField with choices ('message', 'system')
- `title`: CharField (notification title)
- `content`: TextField (notification content)
- `is_read`: BooleanField (whether notification has been read)
- `created_at`: DateTimeField (when notification was created)

## Signals

The system uses Django's `pre_save` and `post_save` signals to automatically track edits and create notifications:

1. **log_message_edit** (pre_save): Triggered before a Message is saved
   - Logs the old content of a message before it's updated
   - Creates a MessageHistory record with the previous version
   - Marks the message as edited with timestamp

2. **create_message_notification** (post_save): Triggered when a new Message is created
   - Creates a notification for the message receiver
   - Sets appropriate title and content
   - Links the notification to the message

3. **handle_message_edit** (post_save): Triggered when a Message is updated
   - Creates edit notifications for message receivers
   - Notifies users when messages they received are edited

4. **update_message_read_status** (post_save): Triggered when a Message is updated
   - Marks related notifications as read when message is marked as read

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Run Tests**:
   ```bash
   python manage.py test messaging
   ```

## Usage Examples

### Creating Messages (via Django Shell)

```python
from django.contrib.auth.models import User
from messaging.models import Message

# Create users
user1 = User.objects.create_user('alice', 'alice@example.com', 'password123')
user2 = User.objects.create_user('bob', 'bob@example.com', 'password123')

# Send a message (this will automatically create a notification)
message = Message.objects.create(
    sender=user1,
    receiver=user2,
    content='Hello Bob! How are you?'
)

# Check that notification was created
from messaging.models import Notification
notification = Notification.objects.get(message=message)
print(f"Notification created for {notification.user.username}")
```

### Editing Messages with History Tracking

```python
# Edit a message (this will automatically create history and notifications)
message.content = 'Hello Bob! How are you doing?'
message.save()

# Check that history was created
from messaging.models import MessageHistory
history = MessageHistory.objects.latest('edited_at')
print(f"Edit logged: '{history.old_content}' by {history.edited_by.username}")

# Check that edit notification was created
edit_notification = Notification.objects.filter(
    message=message,
    notification_type='edit'
).latest('created_at')
print(f"Edit notification created for {edit_notification.user.username}")

# View complete edit history
history_records = MessageHistory.objects.filter(message=message).order_by('edited_at')
for record in history_records:
    print(f"Edit by {record.edited_by.username} at {record.edited_at}: '{record.old_content}'")
```

### Creating System Notifications

```python
from messaging.signals import create_system_notification

# Create a system notification
create_system_notification(
    user=user1,
    title='System Update',
    content='The system will be down for maintenance.'
)
```

### Checking Notifications

```python
# Get all notifications for a user
notifications = Notification.objects.filter(user=user2)

# Get unread notifications
unread_notifications = Notification.objects.filter(
    user=user2,
    is_read=False
)

# Mark a notification as read
notification = Notification.objects.get(id=1)
notification.mark_as_read()
```

## Admin Interface

The Django admin interface provides full management capabilities:

- **Message Admin**: View, create, edit, and delete messages with inline history display
- **MessageHistory Admin**: View and manage message edit history
- **Notification Admin**: View, create, edit, and delete notifications
- **Bulk Actions**: Mark multiple messages/notifications as read/unread/edited
- **Filtering**: Filter by user, notification type, read status, edit status, etc.
- **Search**: Search by username, message content, notification content, history content
- **Inline History**: View message edit history directly in the message admin

## Testing

The project includes comprehensive tests covering:

- **Model Tests**: Message, Notification, and MessageHistory model functionality
- **Signal Tests**: Automatic notification creation, message editing, and history tracking
- **Integration Tests**: Complete messaging flows with editing scenarios
- **Edit Tests**: Message editing functionality and history tracking

Run tests with:
```bash
python manage.py test messaging
```

**Test Coverage**: 27 test cases covering all functionality including message editing and history tracking.

## Key Features

1. **Automatic Notifications**: When a message is created, a notification is automatically created for the receiver
2. **Message Editing**: Support for editing messages with automatic history tracking
3. **Edit History**: Complete history of all message edits with timestamps and user tracking
4. **Edit Notifications**: Automatic notifications when messages are edited
5. **Read Status Tracking**: When a message is marked as read, related notifications are also marked as read
6. **System Notifications**: Utility function for creating system-wide notifications
7. **Admin Integration**: Full Django admin support with custom actions and inline history
8. **Comprehensive Testing**: Unit and integration tests for all functionality including editing

## Signal Implementation Details

The signals are implemented in `messaging/signals.py`:

### Message Creation Signal
```python
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message',
            title=f'New message from {instance.sender.username}',
            content=f'You received a new message: "{instance.get_short_content()}"'
        )
```

### Message Editing Signal
```python
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Only for existing messages
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                # Content has changed, log the old version
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content,
                    edited_by=instance.sender,
                    edited_at=timezone.now()
                )
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
        except Message.DoesNotExist:
            pass
```

### Edit Notification Signal
```python
@receiver(post_save, sender=Message)
def handle_message_edit(sender, instance, created, **kwargs):
    if not created and instance.edited:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='edit',
            title=f'Message edited by {instance.sender.username}',
            content=f'Message was edited: "{instance.get_short_content()}"'
        )
```

This ensures that:
- Every time a new message is created, the receiver automatically gets notified
- Every time a message is edited, the old content is logged and the receiver gets notified
- Complete edit history is maintained with timestamps and user tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the ALX Backend Python curriculum. 