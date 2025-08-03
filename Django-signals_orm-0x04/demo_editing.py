#!/usr/bin/env python3
"""
Demonstration script for the Django Messaging System with Message Editing.

This script demonstrates how the messaging system works with message editing
and history tracking using Django signals.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory
from messaging.signals import create_system_notification


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("Django Messaging System with Message Editing and History Tracking")
    print("=" * 70)
    
    # Clean up any existing test data
    print("\n1. Cleaning up existing test data...")
    User.objects.filter(username__in=['alice', 'bob', 'charlie']).delete()
    
    # Create test users
    print("\n2. Creating test users...")
    alice = User.objects.create_user('alice', 'alice@example.com', 'password123')
    bob = User.objects.create_user('bob', 'bob@example.com', 'password123')
    charlie = User.objects.create_user('charlie', 'charlie@example.com', 'password123')
    
    print(f"   Created users: {alice.username}, {bob.username}, {charlie.username}")
    
    # Demonstrate message creation and editing
    print("\n3. Demonstrating message editing with history tracking...")
    print("   Creating original message...")
    
    message = Message.objects.create(
        sender=alice,
        receiver=bob,
        content='Hello Bob! How are you doing today?'
    )
    
    print(f"   ✓ Message created: {message.content}")
    print(f"   ✓ Message edited status: {message.edited}")
    
    # First edit
    print("\n   Editing message (first edit)...")
    original_content = message.content
    message.content = 'Hello Bob! How are you doing today? I hope you are well.'
    message.save()
    
    print(f"   ✓ Message updated: {message.content}")
    print(f"   ✓ Message edited status: {message.edited}")
    print(f"   ✓ Message edited at: {message.edited_at}")
    
    # Check history
    history1 = MessageHistory.objects.latest('edited_at')
    print(f"   ✓ History record created with old content: '{history1.old_content}'")
    
    # Second edit
    print("\n   Editing message (second edit)...")
    message.content = 'Hello Bob! How are you doing today? I hope you are well. Let me know when you are free to chat.'
    message.save()
    
    print(f"   ✓ Message updated: {message.content}")
    
    # Check history
    history2 = MessageHistory.objects.latest('edited_at')
    print(f"   ✓ History record created with old content: '{history2.old_content}'")
    
    # Third edit
    print("\n   Editing message (third edit)...")
    message.content = 'Hello Bob! How are you doing today? I hope you are well. Let me know when you are free to chat. Looking forward to hearing from you!'
    message.save()
    
    print(f"   ✓ Message updated: {message.content}")
    
    # Check history
    history3 = MessageHistory.objects.latest('edited_at')
    print(f"   ✓ History record created with old content: '{history3.old_content}'")
    
    # Show all history records
    print("\n4. Message Edit History:")
    history_records = MessageHistory.objects.filter(message=message).order_by('edited_at')
    for i, record in enumerate(history_records, 1):
        print(f"   Edit {i}: '{record.old_content}' (by {record.edited_by.username} at {record.edited_at})")
    
    # Show notifications
    print("\n5. Notifications created:")
    notifications = Notification.objects.filter(message=message).order_by('created_at')
    for i, notification in enumerate(notifications, 1):
        print(f"   Notification {i}: {notification.notification_type} - {notification.title}")
        print(f"     Content: {notification.content}")
        print(f"     For user: {notification.user.username}")
        print(f"     Read status: {notification.is_read}")
    
    # Demonstrate system notifications
    print("\n6. Demonstrating system notifications...")
    create_system_notification(
        user=charlie,
        title='System Maintenance',
        content='The messaging system will be down for maintenance on Sunday at 2 AM.'
    )
    
    system_notification = Notification.objects.filter(
        user=charlie,
        notification_type='system'
    ).first()
    
    print(f"   ✓ System notification created for {system_notification.user.username}")
    print(f"   ✓ System notification title: {system_notification.title}")
    
    # Show statistics
    print("\n7. System Statistics:")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total notifications: {Notification.objects.count()}")
    print(f"   Total message history records: {MessageHistory.objects.count()}")
    print(f"   Edited messages: {Message.objects.filter(edited=True).count()}")
    print(f"   Unread notifications: {Notification.objects.filter(is_read=False).count()}")
    
    # Show notifications by type
    print("\n8. Notifications by type:")
    for notification_type in ['message', 'edit', 'system']:
        count = Notification.objects.filter(notification_type=notification_type).count()
        print(f"   {notification_type.capitalize()} notifications: {count}")
    
    # Show notifications for each user
    print("\n9. Notifications by user:")
    for user in [alice, bob, charlie]:
        notifications = Notification.objects.filter(user=user)
        unread_count = notifications.filter(is_read=False).count()
        print(f"   {user.username}: {notifications.count()} total, {unread_count} unread")
    
    print("\n" + "=" * 70)
    print("Message Editing Demonstration completed successfully!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("✓ Automatic history tracking when messages are edited")
    print("✓ Pre-save signal logging old content before updates")
    print("✓ Edit notifications for message receivers")
    print("✓ Message edit status tracking")
    print("✓ Complete edit history with timestamps")
    print("✓ System notifications for administrative purposes")
    print("✓ Proper relationships between messages, history, and notifications")


if __name__ == '__main__':
    main() 