#!/usr/bin/env python3
"""
Demonstration script for the Django Messaging System with Automatic Notifications.

This script demonstrates how the messaging system works with Django signals
to automatically create notifications when messages are sent.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, Notification
from messaging.signals import create_system_notification


def main():
    """Main demonstration function."""
    print("=" * 60)
    print("Django Messaging System with Automatic Notifications")
    print("=" * 60)
    
    # Clean up any existing test data
    print("\n1. Cleaning up existing test data...")
    User.objects.filter(username__in=['alice', 'bob', 'charlie']).delete()
    
    # Create test users
    print("\n2. Creating test users...")
    alice = User.objects.create_user('alice', 'alice@example.com', 'password123')
    bob = User.objects.create_user('bob', 'bob@example.com', 'password123')
    charlie = User.objects.create_user('charlie', 'charlie@example.com', 'password123')
    
    print(f"   Created users: {alice.username}, {bob.username}, {charlie.username}")
    
    # Demonstrate message sending and automatic notification creation
    print("\n3. Demonstrating automatic notification creation...")
    print("   Sending message from Alice to Bob...")
    
    message1 = Message.objects.create(
        sender=alice,
        receiver=bob,
        content='Hello Bob! How are you doing today?'
    )
    
    # Check that notification was automatically created
    notification1 = Notification.objects.get(message=message1)
    print(f"   ✓ Notification automatically created for {notification1.user.username}")
    print(f"   ✓ Notification title: {notification1.title}")
    print(f"   ✓ Notification content: {notification1.content}")
    
    # Send another message
    print("\n   Sending message from Bob to Alice...")
    message2 = Message.objects.create(
        sender=bob,
        receiver=alice,
        content='Hi Alice! I am doing well, thank you for asking!'
    )
    
    notification2 = Notification.objects.get(message=message2)
    print(f"   ✓ Notification automatically created for {notification2.user.username}")
    print(f"   ✓ Notification title: {notification2.title}")
    
    # Demonstrate system notifications
    print("\n4. Demonstrating system notifications...")
    create_system_notification(
        user=charlie,
        title='System Maintenance',
        content='The system will be down for maintenance on Sunday at 2 AM.'
    )
    
    system_notification = Notification.objects.filter(
        user=charlie,
        notification_type='system'
    ).first()
    
    print(f"   ✓ System notification created for {system_notification.user.username}")
    print(f"   ✓ System notification title: {system_notification.title}")
    
    # Demonstrate read status tracking
    print("\n5. Demonstrating read status tracking...")
    print("   Marking Alice's message as read...")
    message2.is_read = True
    message2.save()
    
    # Check that notification is also marked as read
    notification2.refresh_from_db()
    print(f"   ✓ Message marked as read: {message2.is_read}")
    print(f"   ✓ Notification marked as read: {notification2.is_read}")
    
    # Show statistics
    print("\n6. System Statistics:")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total notifications: {Notification.objects.count()}")
    print(f"   Unread notifications: {Notification.objects.filter(is_read=False).count()}")
    
    # Show notifications for each user
    print("\n7. Notifications by user:")
    for user in [alice, bob, charlie]:
        notifications = Notification.objects.filter(user=user)
        unread_count = notifications.filter(is_read=False).count()
        print(f"   {user.username}: {notifications.count()} total, {unread_count} unread")
    
    print("\n" + "=" * 60)
    print("Demonstration completed successfully!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✓ Automatic notification creation when messages are sent")
    print("✓ System notifications for administrative purposes")
    print("✓ Read status tracking between messages and notifications")
    print("✓ Proper relationships between users, messages, and notifications")
    print("✓ Django signals working correctly")


if __name__ == '__main__':
    main() 