from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Message, Notification
from .signals import create_system_notification


class MessageModelTest(TestCase):
    """Test cases for the Message model."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_message_creation(self):
        """Test creating a message."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, this is a test message!'
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Hello, this is a test message!')
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.timestamp)
    
    def test_message_str_representation(self):
        """Test the string representation of a message."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        
        expected_str = f"Message from {self.user1.username} to {self.user2.username} at {message.timestamp}"
        self.assertEqual(str(message), expected_str)
    
    def test_get_short_content(self):
        """Test the get_short_content method."""
        # Test with short content
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Short message'
        )
        self.assertEqual(message1.get_short_content(), 'Short message')
        
        # Test with long content
        long_content = 'This is a very long message that should be truncated when displayed in the admin interface or other places where space is limited.'
        message2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content=long_content
        )
        self.assertEqual(message2.get_short_content(), 'This is a very long message that should be truncat...')
    
    def test_message_ordering(self):
        """Test that messages are ordered by timestamp (newest first)."""
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='First message'
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Second message'
        )
        
        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)  # Newest first
        self.assertEqual(messages[1], message1)


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='New Message',
            content='You have received a new message.'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.notification_type, 'message')
        self.assertEqual(notification.title, 'New Message')
        self.assertEqual(notification.content, 'You have received a new message.')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_notification_with_message(self):
        """Test creating a notification linked to a message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.user,
            content='Test message'
        )
        
        notification = Notification.objects.create(
            user=self.user,
            message=message,
            notification_type='message',
            title='New Message',
            content='You have received a new message.'
        )
        
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.user, self.user)
    
    def test_notification_str_representation(self):
        """Test the string representation of a notification."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='Test Notification',
            content='Test content'
        )
        
        expected_str = f"Notification for {self.user.username}: Test Notification"
        self.assertEqual(str(notification), expected_str)
    
    def test_mark_as_read(self):
        """Test marking a notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='Test Notification',
            content='Test content'
        )
        
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at (newest first)."""
        notification1 = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='First Notification',
            content='First content'
        )
        notification2 = Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='Second Notification',
            content='Second content'
        )
        
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], notification2)  # Newest first
        self.assertEqual(notifications[1], notification1)


class SignalTest(TestCase):
    """Test cases for Django signals."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_message_creation_triggers_notification(self):
        """Test that creating a message automatically creates a notification."""
        initial_notification_count = Notification.objects.count()
        
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, this is a test message!'
        )
        
        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)
        
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertEqual(notification.title, f'New message from {self.user1.username}')
        self.assertIn('Hello, this is a test message!', notification.content)
    
    def test_message_update_does_not_create_notification(self):
        """Test that updating a message does not create a new notification."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        initial_notification_count = Notification.objects.count()
        
        # Update the message
        message.content = 'Updated message'
        message.save()
        
        # Check that no new notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count)
    
    def test_message_read_status_updates_notification(self):
        """Test that marking a message as read updates notification status."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        
        # Get the notification that was created
        notification = Notification.objects.get(message=message)
        self.assertFalse(notification.is_read)
        
        # Mark the message as read
        message.is_read = True
        message.save()
        
        # Check that the notification is now marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_system_notification_creation(self):
        """Test the create_system_notification utility function."""
        from .signals import create_system_notification
        
        initial_notification_count = Notification.objects.count()
        
        create_system_notification(
            user=self.user1,
            title='System Update',
            content='This is a system notification.'
        )
        
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)
        
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.notification_type, 'system')
        self.assertEqual(notification.title, 'System Update')
        self.assertEqual(notification.content, 'This is a system notification.')
        self.assertFalse(notification.is_read)


class IntegrationTest(TestCase):
    """Integration tests for the messaging system."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='charlie',
            email='charlie@example.com',
            password='testpass123'
        )
    
    def test_complete_messaging_flow(self):
        """Test a complete messaging flow with notifications."""
        # User1 sends a message to User2
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello Bob! How are you?'
        )
        
        # Check that notification was created for User2
        notification1 = Notification.objects.get(message=message1)
        self.assertEqual(notification1.user, self.user2)
        self.assertFalse(notification1.is_read)
        
        # User2 sends a reply to User1
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Hi Alice! I am doing well, thank you!'
        )
        
        # Check that notification was created for User1
        notification2 = Notification.objects.get(message=message2)
        self.assertEqual(notification2.user, self.user1)
        self.assertFalse(notification2.is_read)
        
        # User1 marks the message as read
        message2.is_read = True
        message2.save()
        
        # Check that the notification is now marked as read
        notification2.refresh_from_db()
        self.assertTrue(notification2.is_read)
        
        # Check that User2 has one unread notification
        unread_notifications = Notification.objects.filter(
            user=self.user2,
            is_read=False
        )
        self.assertEqual(unread_notifications.count(), 1)
        
        # Check that User1 has no unread notifications
        unread_notifications = Notification.objects.filter(
            user=self.user1,
            is_read=False
        )
        self.assertEqual(unread_notifications.count(), 0)
    
    def test_multiple_messages_same_users(self):
        """Test sending multiple messages between the same users."""
        # Send multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                content=f'Message {i + 1} from Alice'
            )
        
        # Check that 3 notifications were created
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 3)
        
        # Check that all notifications are unread
        unread_notifications = notifications.filter(is_read=False)
        self.assertEqual(unread_notifications.count(), 3) 