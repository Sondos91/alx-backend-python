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

### Notification Model
- `user`: ForeignKey to User (who gets the notification)
- `message`: ForeignKey to Message (optional link to related message)
- `notification_type`: CharField with choices ('message', 'system')
- `title`: CharField (notification title)
- `content`: TextField (notification content)
- `is_read`: BooleanField (whether notification has been read)
- `created_at`: DateTimeField (when notification was created)

## Signals

The system uses Django's `post_save` signal to automatically create notifications:

1. **create_message_notification**: Triggered when a new Message is created
   - Creates a notification for the message receiver
   - Sets appropriate title and content
   - Links the notification to the message

2. **update_message_read_status**: Triggered when a Message is updated
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

- **Message Admin**: View, create, edit, and delete messages
- **Notification Admin**: View, create, edit, and delete notifications
- **Bulk Actions**: Mark multiple notifications as read/unread
- **Filtering**: Filter by user, notification type, read status, etc.
- **Search**: Search by username, message content, notification content

## Testing

The project includes comprehensive tests covering:

- **Model Tests**: Message and Notification model functionality
- **Signal Tests**: Automatic notification creation and updates
- **Integration Tests**: Complete messaging flows

Run tests with:
```bash
python manage.py test messaging
```

## Key Features

1. **Automatic Notifications**: When a message is created, a notification is automatically created for the receiver
2. **Read Status Tracking**: When a message is marked as read, related notifications are also marked as read
3. **System Notifications**: Utility function for creating system-wide notifications
4. **Admin Integration**: Full Django admin support with custom actions
5. **Comprehensive Testing**: Unit and integration tests for all functionality

## Signal Implementation Details

The signals are implemented in `messaging/signals.py`:

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

This ensures that every time a new message is created, the receiver automatically gets notified.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the ALX Backend Python curriculum. 