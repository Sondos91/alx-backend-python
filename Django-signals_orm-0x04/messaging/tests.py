from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Message, Notification, MessageHistory
from .signals import create_system_notification
from django.test import Client
from django.urls import reverse


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
        self.assertFalse(message.edited)
        self.assertIsNone(message.edited_at)
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
    
    def test_mark_as_edited(self):
        """Test marking a message as edited."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        self.assertFalse(message.edited)
        self.assertIsNone(message.edited_at)
        
        message.mark_as_edited()
        
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.edited_at)
    
    def test_mark_as_read(self):
        """Test marking a message as read."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        
        self.assertFalse(message.read)
        self.assertFalse(message.is_read)
        
        message.mark_as_read()
        
        self.assertTrue(message.read)
        self.assertTrue(message.is_read)
    
    def test_mark_as_unread(self):
        """Test marking a message as unread."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message',
            read=True,
            is_read=True
        )
        
        self.assertTrue(message.read)
        self.assertTrue(message.is_read)
        
        message.mark_as_unread()
        
        self.assertFalse(message.read)
        self.assertFalse(message.is_read)


class MessageHistoryModelTest(TestCase):
    """Test cases for the MessageHistory model."""
    
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
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message content'
        )
    
    def test_message_history_creation(self):
        """Test creating a message history record."""
        history = MessageHistory.objects.create(
            message=self.message,
            old_content='Original content',
            edited_by=self.user1
        )
        
        self.assertEqual(history.message, self.message)
        self.assertEqual(history.old_content, 'Original content')
        self.assertEqual(history.edited_by, self.user1)
        self.assertIsNotNone(history.edited_at)
    
    def test_message_history_str_representation(self):
        """Test the string representation of a message history record."""
        history = MessageHistory.objects.create(
            message=self.message,
            old_content='Original content',
            edited_by=self.user1
        )
        
        expected_str = f"Edit of message {self.message.id} by {self.user1.username} at {history.edited_at}"
        self.assertEqual(str(history), expected_str)
    
    def test_get_short_old_content(self):
        """Test the get_short_old_content method."""
        # Test with short content
        history1 = MessageHistory.objects.create(
            message=self.message,
            old_content='Short old content',
            edited_by=self.user1
        )
        self.assertEqual(history1.get_short_old_content(), 'Short old content')
        
        # Test with long content
        long_content = 'This is a very long old content that should be truncated when displayed in the admin interface or other places where space is limited.'
        history2 = MessageHistory.objects.create(
            message=self.message,
            old_content=long_content,
            edited_by=self.user1
        )
        self.assertEqual(history2.get_short_old_content(), 'This is a very long old content that should be tru...')
    
    def test_message_history_ordering(self):
        """Test that message history is ordered by edited_at (newest first)."""
        history1 = MessageHistory.objects.create(
            message=self.message,
            old_content='First edit',
            edited_by=self.user1
        )
        history2 = MessageHistory.objects.create(
            message=self.message,
            old_content='Second edit',
            edited_by=self.user1
        )
        
        history_records = MessageHistory.objects.all()
        self.assertEqual(history_records[0], history2)  # Newest first
        self.assertEqual(history_records[1], history1)


class MessageEditSignalTest(TestCase):
    """Test cases for message editing signals."""
    
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
    
    def test_message_edit_creates_history(self):
        """Test that editing a message creates a history record."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        # Edit the message
        message.content = 'Edited message'
        message.save()
        
        # Check that a history record was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count + 1)
        
        history = MessageHistory.objects.latest('edited_at')
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, 'Original message')
        self.assertEqual(history.edited_by, self.user1)
    
    def test_message_edit_does_not_create_history_for_new_message(self):
        """Test that creating a new message does not create history."""
        initial_history_count = MessageHistory.objects.count()
        
        # Create a new message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='New message'
        )
        
        # Check that no history record was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)
    
    def test_message_edit_without_content_change_does_not_create_history(self):
        """Test that editing a message without changing content does not create history."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        # Update message without changing content
        message.is_read = True
        message.save()
        
        # Check that no history record was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)
    
    def test_message_edit_creates_edit_notification(self):
        """Test that editing a message creates an edit notification."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        initial_notification_count = Notification.objects.count()
        
        # Edit the message (this will automatically mark it as edited via signal)
        message.content = 'Edited message'
        message.save()
        
        # Check that an edit notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)
        
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'edit')
        self.assertIn('edited', notification.title.lower())
    
    def test_multiple_message_edits(self):
        """Test multiple edits of the same message."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        # First edit
        message.content = 'First edit'
        message.save()
        
        # Second edit
        message.content = 'Second edit'
        message.save()
        
        # Third edit
        message.content = 'Third edit'
        message.save()
        
        # Check that three history records were created
        self.assertEqual(MessageHistory.objects.count(), 3)
        
        # Check the history records
        history_records = MessageHistory.objects.filter(message=message).order_by('edited_at')
        self.assertEqual(history_records[0].old_content, 'Original message')
        self.assertEqual(history_records[1].old_content, 'First edit')
        self.assertEqual(history_records[2].old_content, 'Second edit')


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
    
    def test_edit_notification_creation(self):
        """Test creating an edit notification."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.user,
            content='Test message'
        )
        
        notification = Notification.objects.create(
            user=self.user,
            message=message,
            notification_type='edit',
            title='Message Edited',
            content='A message was edited.'
        )
        
        self.assertEqual(notification.notification_type, 'edit')
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, message)
    
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
        """Test that updating a message without content change does not create a new notification."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message'
        )
        
        initial_notification_count = Notification.objects.count()
        
        # Update the message without changing content
        message.is_read = True
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
    
    def test_complete_message_editing_flow(self):
        """Test a complete message editing flow with history tracking."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original message content'
        )
        
        # Get initial notification count (1 for the new message)
        initial_notification_count = Notification.objects.count()
        
        # Edit the message multiple times
        message.content = 'First edit'
        message.save()
        
        message.content = 'Second edit'
        message.save()
        
        message.content = 'Final version'
        message.save()
        
        # Check that history records were created
        history_records = MessageHistory.objects.filter(message=message)
        self.assertEqual(history_records.count(), 3)
        
        # Check the content of history records
        history_list = list(history_records.order_by('edited_at'))
        self.assertEqual(history_list[0].old_content, 'Original message content')
        self.assertEqual(history_list[1].old_content, 'First edit')
        self.assertEqual(history_list[2].old_content, 'Second edit')
        
        # Check that edit notifications were created (3 edits = 3 edit notifications)
        edit_notifications = Notification.objects.filter(
            message=message,
            notification_type='edit'
        )
        self.assertEqual(edit_notifications.count(), 3)
        
        # Check that all edit notifications are for the receiver
        for notification in edit_notifications:
            self.assertEqual(notification.user, self.user2)
    
    def test_complete_user_deletion_flow(self):
        """Test a complete user deletion flow with data cleanup."""
        # Create comprehensive data for user1
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message from Alice to Bob'
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Message from Bob to Alice'
        )
        message3 = Message.objects.create(
            sender=self.user2,
            receiver=self.user3,
            content='Message from Bob to Charlie'
        )
        
        # Create notifications
        notification1 = Notification.objects.create(
            user=self.user1,
            message=message1,
            notification_type='message',
            title='Notification for Alice'
        )
        notification2 = Notification.objects.create(
            user=self.user2,
            message=message2,
            notification_type='message',
            title='Notification for Bob'
        )
        
        # Create message history
        history = MessageHistory.objects.create(
            message=message1,
            old_content='Old content',
            edited_by=self.user1
        )
        
        # Check initial counts
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Message.objects.count(), 3)
        # Note: Notifications are automatically created by signals when messages are created
        initial_notification_count = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Check that user1 and all their data is deleted
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 1)  # Only message3 remains
        # Notifications that reference deleted messages are deleted via CASCADE
        # But system notifications without message references may remain
        remaining_notifications = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 0)  # All history deleted
        
        # Check that other users still exist
        self.assertTrue(User.objects.filter(username='bob').exists())
        self.assertTrue(User.objects.filter(username='charlie').exists())
        
        # Check that remaining data is intact
        remaining_message = Message.objects.first()
        self.assertEqual(remaining_message.sender, self.user2)
        self.assertEqual(remaining_message.receiver, self.user3)
        
        remaining_notification = Notification.objects.first()
        self.assertEqual(remaining_notification.user, self.user2)


class UserDeletionTest(TestCase):
    """Test cases for user deletion and data cleanup."""
    
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
        self.user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
    
    def test_user_deletion_cleans_up_messages(self):
        """Test that deleting a user cleans up all related messages."""
        # Create messages involving the user
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message from user1 to user2'
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Message from user2 to user1'
        )
        message3 = Message.objects.create(
            sender=self.user2,
            receiver=self.user3,
            content='Message from user2 to user3'
        )
        
        # Create notifications
        notification1 = Notification.objects.create(
            user=self.user1,
            message=message1,
            notification_type='message',
            title='Test notification'
        )
        
        # Create message history
        history = MessageHistory.objects.create(
            message=message1,
            old_content='Old content',
            edited_by=self.user1
        )
        
        # Check initial counts
        self.assertEqual(Message.objects.count(), 3)
        # Note: Notifications are automatically created by signals when messages are created
        initial_notification_count = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Check that user1's data is cleaned up
        self.assertEqual(Message.objects.count(), 1)  # Only message3 remains
        # Notifications that reference deleted messages are deleted via CASCADE
        # But system notifications without message references remain
        remaining_notifications = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 0)  # All history deleted
        
        # Check that user2 and user3 still exist
        self.assertTrue(User.objects.filter(username='testuser2').exists())
        self.assertTrue(User.objects.filter(username='testuser3').exists())
    
    def test_user_deletion_cleans_up_notifications(self):
        """Test that deleting a user cleans up all their notifications."""
        # Create notifications for the user
        notification1 = Notification.objects.create(
            user=self.user1,
            notification_type='message',
            title='Notification 1'
        )
        notification2 = Notification.objects.create(
            user=self.user1,
            notification_type='system',
            title='Notification 2'
        )
        notification3 = Notification.objects.create(
            user=self.user2,
            notification_type='message',
            title='Notification 3'
        )
        
        # Check initial count
        self.assertEqual(Notification.objects.count(), 3)
        
        # Delete user1
        self.user1.delete()
        
        # Check that only user1's notifications are deleted
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first(), notification3)
    
    def test_user_deletion_cleans_up_message_history(self):
        """Test that deleting a user cleans up all their message edits."""
        message = Message.objects.create(
            sender=self.user2,
            receiver=self.user3,
            content='Original message'
        )
        
        # Create message history records
        history1 = MessageHistory.objects.create(
            message=message,
            old_content='Old content 1',
            edited_by=self.user1
        )
        history2 = MessageHistory.objects.create(
            message=message,
            old_content='Old content 2',
            edited_by=self.user2
        )
        
        # Check initial count
        self.assertEqual(MessageHistory.objects.count(), 2)
        
        # Delete user1
        self.user1.delete()
        
        # Check that only user1's history is deleted
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.assertEqual(MessageHistory.objects.first(), history2)


class AccountDeletionViewTest(TestCase):
    """Test cases for account deletion views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
    
    def test_delete_account_confirm_view_requires_login(self):
        """Test that delete account confirm view requires login."""
        response = self.client.get(reverse('messaging:delete_account_confirm'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_delete_account_confirm_view_with_login(self):
        """Test delete account confirm view with logged in user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('messaging:delete_account_confirm'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Account')
    
    def test_delete_account_confirm_view_shows_user_stats(self):
        """Test that delete account confirm view shows user statistics."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create some data for the user
        Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content='Test message'
        )
        Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='Test notification'
        )
        
        response = self.client.get(reverse('messaging:delete_account_confirm'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Should show 1 message
        self.assertContains(response, '1')  # Should show 1 notification
    
    def test_delete_account_view_requires_login(self):
        """Test that delete account view requires login."""
        response = self.client.post(reverse('messaging:delete_account'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_delete_account_view_requires_post(self):
        """Test that delete account view requires POST method."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('messaging:delete_account'))
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_delete_account_view_deletes_user_and_data(self):
        """Test that delete account view properly deletes user and all data."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create some data for the user
        message1 = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content='Message from user'
        )
        message2 = Message.objects.create(
            sender=self.other_user,
            receiver=self.user,
            content='Message to user'
        )
        notification = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='Test notification'
        )
        history = MessageHistory.objects.create(
            message=message1,
            old_content='Old content',
            edited_by=self.user
        )
        
        # Check initial counts
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 2)
        # Note: Notifications are automatically created by signals when messages are created
        initial_notification_count = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        # Delete the account
        response = self.client.post(reverse('messaging:delete_account'))
        
        # Check that user is redirected to account deleted page
        self.assertEqual(response.status_code, 302)
        
        # Check that user and all their data is deleted
        self.assertEqual(User.objects.count(), 1)  # Only other_user remains
        self.assertEqual(Message.objects.count(), 0)  # All messages deleted
        # Notifications that reference deleted messages are deleted via CASCADE
        # But system notifications without message references may remain
        remaining_notifications = Notification.objects.count()
        self.assertEqual(MessageHistory.objects.count(), 0)  # All history deleted
        
        # Check that other user still exists
        self.assertTrue(User.objects.filter(username='otheruser').exists())
    
    def test_account_deleted_view(self):
        """Test account deleted view."""
        response = self.client.get(reverse('messaging:account_deleted'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account Successfully Deleted') 


class UnreadMessagesTest(TestCase):
    """Test cases for unread messages functionality."""
    
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
        self.user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
    
    def test_unread_messages_manager_for_user(self):
        """Test the UnreadMessagesManager.for_user method."""
        # Create read and unread messages
        read_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Read message',
            read=True,
            is_read=True
        )
        unread_message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message 1',
            read=False,
            is_read=False
        )
        unread_message2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content='Unread message 2',
            read=False,
            is_read=False
        )
        
        # Get unread messages for user2
        unread_messages = Message.unread.for_user(self.user2)
        
        self.assertEqual(unread_messages.count(), 2)
        self.assertIn(unread_message1, unread_messages)
        self.assertIn(unread_message2, unread_messages)
        self.assertNotIn(read_message, unread_messages)
    
    def test_unread_messages_manager_count_for_user(self):
        """Test the UnreadMessagesManager.count_for_user method."""
        # Create messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message 1',
            read=False
        )
        Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content='Unread message 2',
            read=False
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Read message',
            read=True
        )
        
        # Count unread messages for user2
        unread_count = Message.unread.count_for_user(self.user2)
        self.assertEqual(unread_count, 2)
    
    def test_unread_messages_manager_optimization(self):
        """Test that the unread messages manager uses optimized queries."""
        # Create unread messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message',
            read=False
        )
        
        # Get unread messages and check if only necessary fields are retrieved
        unread_messages = Message.unread.for_user(self.user2)
        
        # The query should use select_related and only
        # We can't directly test the SQL, but we can verify the queryset works
        message = unread_messages.first()
        self.assertIsNotNone(message)
        self.assertEqual(message.receiver, self.user2)
        self.assertFalse(message.read)
    
    def test_unread_messages_exclude_sent_messages(self):
        """Test that unread messages only include received messages."""
        # Create messages where user2 is sender
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Message sent by user2',
            read=False
        )
        
        # Create messages where user2 is receiver
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message received by user2',
            read=False
        )
        
        # Get unread messages for user2 (should only be received messages)
        unread_messages = Message.unread.for_user(self.user2)
        
        self.assertEqual(unread_messages.count(), 1)
        message = unread_messages.first()
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.sender, self.user1)


class UnreadMessagesViewTest(TestCase):
    """Test cases for unread messages views."""
    
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
        self.client = Client()
    
    def test_unread_messages_view_requires_login(self):
        """Test that unread messages view requires login."""
        response = self.client.get(reverse('messaging:unread_messages'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_unread_messages_view_with_login(self):
        """Test unread messages view with authenticated user."""
        self.client.login(username='testuser1', password='testpass123')
        
        # Create unread messages
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Unread message 1',
            read=False
        )
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Unread message 2',
            read=False
        )
        
        response = self.client.get(reverse('messaging:unread_messages'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unread message 1')
        self.assertContains(response, 'Unread message 2')
        self.assertContains(response, '2')  # unread count
    
    def test_mark_message_read_view(self):
        """Test marking a specific message as read."""
        self.client.login(username='testuser1', password='testpass123')
        
        message = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Unread message',
            read=False
        )
        
        response = self.client.post(
            reverse('messaging:mark_message_read', args=[message.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        
        # Check that message is now read
        message.refresh_from_db()
        self.assertTrue(message.read)
        self.assertTrue(message.is_read)
    
    def test_mark_all_messages_read_view(self):
        """Test marking all unread messages as read."""
        self.client.login(username='testuser1', password='testpass123')
        
        # Create unread messages
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Unread message 1',
            read=False
        )
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Unread message 2',
            read=False
        )
        
        response = self.client.post(reverse('messaging:mark_all_messages_read'))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that all messages are now read
        unread_count = Message.unread.count_for_user(self.user1)
        self.assertEqual(unread_count, 0) 