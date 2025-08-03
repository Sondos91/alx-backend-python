#!/usr/bin/env python3
"""
Demonstration script for unread messages functionality.

This script demonstrates:
1. Creating messages with read/unread status
2. Using the custom UnreadMessagesManager
3. Marking messages as read/unread
4. Counting unread messages
5. Optimized queries with .only() and select_related
"""

import os
import sys
import django
from django.utils import timezone

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, Notification


def create_test_users():
    """Create test users for the demonstration."""
    print("Creating test users...")
    
    # Create users if they don't exist
    user1, created = User.objects.get_or_create(
        username='demo_user1',
        defaults={'email': 'user1@demo.com'}
    )
    if created:
        user1.set_password('demo123')
        user1.save()
        print(f"Created user: {user1.username}")
    else:
        print(f"User already exists: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='demo_user2',
        defaults={'email': 'user2@demo.com'}
    )
    if created:
        user2.set_password('demo123')
        user2.save()
        print(f"Created user: {user2.username}")
    else:
        print(f"User already exists: {user2.username}")
    
    user3, created = User.objects.get_or_create(
        username='demo_user3',
        defaults={'email': 'user3@demo.com'}
    )
    if created:
        user3.set_password('demo123')
        user3.save()
        print(f"Created user: {user3.username}")
    else:
        print(f"User already exists: {user3.username}")
    
    return user1, user2, user3


def create_test_messages(user1, user2, user3):
    """Create test messages with different read statuses."""
    print("\nCreating test messages...")
    
    # Clear existing messages for these users
    Message.objects.filter(
        sender__in=[user1, user2, user3],
        receiver__in=[user1, user2, user3]
    ).delete()
    
    # Create read messages
    read_message1 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content='This is a read message from user1 to user2',
        read=True,
        is_read=True
    )
    print(f"Created read message: {read_message1.content[:50]}...")
    
    read_message2 = Message.objects.create(
        sender=user3,
        receiver=user2,
        content='This is another read message from user3 to user2',
        read=True,
        is_read=True
    )
    print(f"Created read message: {read_message2.content[:50]}...")
    
    # Create unread messages
    unread_message1 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content='This is an unread message from user1 to user2',
        read=False,
        is_read=False
    )
    print(f"Created unread message: {unread_message1.content[:50]}...")
    
    unread_message2 = Message.objects.create(
        sender=user3,
        receiver=user2,
        content='This is another unread message from user3 to user2',
        read=False,
        is_read=False
    )
    print(f"Created unread message: {unread_message2.content[:50]}...")
    
    unread_message3 = Message.objects.create(
        sender=user1,
        receiver=user3,
        content='This is an unread message from user1 to user3',
        read=False,
        is_read=False
    )
    print(f"Created unread message: {unread_message3.content[:50]}...")
    
    # Create a message sent by user2 (should not appear in user2's unread messages)
    sent_message = Message.objects.create(
        sender=user2,
        receiver=user1,
        content='This is a message sent by user2 to user1',
        read=False,
        is_read=False
    )
    print(f"Created sent message: {sent_message.content[:50]}...")
    
    return {
        'read_messages': [read_message1, read_message2],
        'unread_messages': [unread_message1, unread_message2, unread_message3],
        'sent_message': sent_message
    }


def demonstrate_unread_messages_manager(user1, user2, user3):
    """Demonstrate the UnreadMessagesManager functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING UNREAD MESSAGES MANAGER")
    print("="*60)
    
    # Get unread messages for user2 using the custom manager
    print(f"\nGetting unread messages for {user2.username}...")
    unread_messages_user2 = Message.unread.for_user(user2)
    
    print(f"Found {unread_messages_user2.count()} unread messages for {user2.username}:")
    for message in unread_messages_user2:
        print(f"  - From {message.sender.username}: {message.content[:50]}...")
    
    # Get unread count for user2
    unread_count_user2 = Message.unread.count_for_user(user2)
    print(f"\nUnread count for {user2.username}: {unread_count_user2}")
    
    # Get unread messages for user3
    print(f"\nGetting unread messages for {user3.username}...")
    unread_messages_user3 = Message.unread.for_user(user3)
    
    print(f"Found {unread_messages_user3.count()} unread messages for {user3.username}:")
    for message in unread_messages_user3:
        print(f"  - From {message.sender.username}: {message.content[:50]}...")
    
    # Get unread count for user3
    unread_count_user3 = Message.unread.count_for_user(user3)
    print(f"\nUnread count for {user3.username}: {unread_count_user3}")
    
    # Verify that sent messages don't appear in unread messages
    print(f"\nVerifying that {user2.username}'s sent messages don't appear in their unread list...")
    user2_sent_messages = Message.objects.filter(sender=user2, read=False)
    print(f"User2 has {user2_sent_messages.count()} unread sent messages")
    
    unread_messages_user2_again = Message.unread.for_user(user2)
    print(f"But only {unread_messages_user2_again.count()} unread received messages")


def demonstrate_mark_as_read(user2, messages):
    """Demonstrate marking messages as read."""
    print("\n" + "="*60)
    print("DEMONSTRATING MARK AS READ FUNCTIONALITY")
    print("="*60)
    
    # Get initial unread count
    initial_unread_count = Message.unread.count_for_user(user2)
    print(f"\nInitial unread count for {user2.username}: {initial_unread_count}")
    
    # Mark first unread message as read
    if messages['unread_messages']:
        message_to_mark = messages['unread_messages'][0]
        print(f"\nMarking message '{message_to_mark.content[:50]}...' as read")
        
        message_to_mark.mark_as_read()
        message_to_mark.refresh_from_db()
        
        print(f"Message read status: {message_to_mark.read}")
        print(f"Message is_read status: {message_to_mark.is_read}")
        
        # Check updated unread count
        updated_unread_count = Message.unread.count_for_user(user2)
        print(f"Updated unread count for {user2.username}: {updated_unread_count}")
        
        # Verify the message no longer appears in unread messages
        unread_messages = Message.unread.for_user(user2)
        print(f"Message in unread list: {message_to_mark in unread_messages}")


def demonstrate_mark_as_unread(user2, messages):
    """Demonstrate marking messages as unread."""
    print("\n" + "="*60)
    print("DEMONSTRATING MARK AS UNREAD FUNCTIONALITY")
    print("="*60)
    
    # Mark a read message as unread
    if messages['read_messages']:
        message_to_mark = messages['read_messages'][0]
        print(f"\nMarking message '{message_to_mark.content[:50]}...' as unread")
        
        message_to_mark.mark_as_unread()
        message_to_mark.refresh_from_db()
        
        print(f"Message read status: {message_to_mark.read}")
        print(f"Message is_read status: {message_to_mark.is_read}")
        
        # Check updated unread count
        updated_unread_count = Message.unread.count_for_user(user2)
        print(f"Updated unread count for {user2.username}: {updated_unread_count}")
        
        # Verify the message now appears in unread messages
        unread_messages = Message.unread.for_user(user2)
        print(f"Message in unread list: {message_to_mark in unread_messages}")


def demonstrate_query_optimization():
    """Demonstrate the query optimization features."""
    print("\n" + "="*60)
    print("DEMONSTRATING QUERY OPTIMIZATION")
    print("="*60)
    
    # Get a user for demonstration
    user = User.objects.first()
    if not user:
        print("No users found for optimization demonstration")
        return
    
    print(f"\nDemonstrating optimized queries for {user.username}...")
    
    # Use the custom manager which includes select_related and only
    unread_messages = Message.unread.for_user(user)
    
    print(f"Retrieved {unread_messages.count()} unread messages")
    print("The custom manager uses:")
    print("  - select_related('sender') for efficient user data retrieval")
    print("  - .only() to retrieve only necessary fields")
    print("  - Database index on (receiver, read) for fast filtering")
    
    # Show the fields that are retrieved
    if unread_messages.exists():
        message = unread_messages.first()
        print(f"\nSample message fields retrieved:")
        print(f"  - ID: {message.id}")
        print(f"  - Sender: {message.sender.username}")
        print(f"  - Content: {message.content[:30]}...")
        print(f"  - Timestamp: {message.timestamp}")
        print(f"  - Read status: {message.read}")


def main():
    """Main demonstration function."""
    print("UNREAD MESSAGES FUNCTIONALITY DEMONSTRATION")
    print("="*60)
    
    # Create test users
    user1, user2, user3 = create_test_users()
    
    # Create test messages
    messages = create_test_messages(user1, user2, user3)
    
    # Demonstrate the unread messages manager
    demonstrate_unread_messages_manager(user1, user2, user3)
    
    # Demonstrate mark as read functionality
    demonstrate_mark_as_read(user2, messages)
    
    # Demonstrate mark as unread functionality
    demonstrate_mark_as_unread(user2, messages)
    
    # Demonstrate query optimization
    demonstrate_query_optimization()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("1. Custom UnreadMessagesManager with optimized queries")
    print("2. .for_user() method to get unread messages for a specific user")
    print("3. .count_for_user() method to get unread message count")
    print("4. .mark_as_read() and .mark_as_unread() methods")
    print("5. Query optimization with select_related and .only()")
    print("6. Database indexing for efficient filtering")
    print("7. Proper filtering (only received messages, not sent)")


if __name__ == '__main__':
    main() 