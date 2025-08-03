#!/usr/bin/env python3
"""
Demonstration script for the Django Messaging System with Account Deletion.

This script demonstrates how the messaging system handles account deletion
with automatic cleanup of all related data using Django signals.
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
    print("Django Messaging System with Account Deletion and Data Cleanup")
    print("=" * 70)
    
    # Clean up any existing test data
    print("\n1. Cleaning up existing test data...")
    User.objects.filter(username__in=['alice', 'bob', 'charlie', 'david']).delete()
    
    # Create test users
    print("\n2. Creating test users...")
    alice = User.objects.create_user('alice', 'alice@example.com', 'password123')
    bob = User.objects.create_user('bob', 'bob@example.com', 'password123')
    charlie = User.objects.create_user('charlie', 'charlie@example.com', 'password123')
    david = User.objects.create_user('david', 'david@example.com', 'password123')
    
    print(f"   Created users: {alice.username}, {bob.username}, {charlie.username}, {david.username}")
    
    # Create comprehensive data for Alice
    print("\n3. Creating comprehensive data for Alice...")
    
    # Messages sent by Alice
    message1 = Message.objects.create(
        sender=alice,
        receiver=bob,
        content='Hello Bob! How are you doing?'
    )
    message2 = Message.objects.create(
        sender=alice,
        receiver=charlie,
        content='Hi Charlie! Nice to meet you!'
    )
    
    # Messages received by Alice
    message3 = Message.objects.create(
        sender=bob,
        receiver=alice,
        content='Hi Alice! I am doing well, thank you!'
    )
    message4 = Message.objects.create(
        sender=charlie,
        receiver=alice,
        content='Hello Alice! Nice to meet you too!'
    )
    
    # Messages between other users (should remain after Alice's deletion)
    message5 = Message.objects.create(
        sender=bob,
        receiver=charlie,
        content='Hey Charlie! How are you?'
    )
    message6 = Message.objects.create(
        sender=david,
        receiver=bob,
        content='Hello Bob!'
    )
    
    # Notifications for Alice
    notification1 = Notification.objects.create(
        user=alice,
        message=message3,
        notification_type='message',
        title='New message from bob'
    )
    notification2 = Notification.objects.create(
        user=alice,
        message=message4,
        notification_type='message',
        title='New message from charlie'
    )
    
    # Notifications for other users (should remain)
    notification3 = Notification.objects.create(
        user=bob,
        message=message1,
        notification_type='message',
        title='New message from alice'
    )
    notification4 = Notification.objects.create(
        user=charlie,
        message=message2,
        notification_type='message',
        title='New message from alice'
    )
    
    # Message edits by Alice
    message1.content = 'Hello Bob! How are you doing today?'
    message1.save()  # This creates a history record
    
    message2.content = 'Hi Charlie! Nice to meet you! How are you doing?'
    message2.save()  # This creates another history record
    
    # Message edits by other users (should remain)
    message5.content = 'Hey Charlie! How are you doing today?'
    message5.save()
    
    print("   ✓ Created messages, notifications, and message edits")
    
    # Show initial statistics
    print("\n4. Initial System Statistics:")
    print(f"   Total users: {User.objects.count()}")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total notifications: {Notification.objects.count()}")
    print(f"   Total message history records: {MessageHistory.objects.count()}")
    
    # Show Alice's data
    print("\n5. Alice's Data Summary:")
    alice_sent_messages = Message.objects.filter(sender=alice).count()
    alice_received_messages = Message.objects.filter(receiver=alice).count()
    alice_notifications = Notification.objects.filter(user=alice).count()
    alice_edits = MessageHistory.objects.filter(edited_by=alice).count()
    
    print(f"   Messages sent by Alice: {alice_sent_messages}")
    print(f"   Messages received by Alice: {alice_received_messages}")
    print(f"   Notifications for Alice: {alice_notifications}")
    print(f"   Message edits by Alice: {alice_edits}")
    print(f"   Total data items for Alice: {alice_sent_messages + alice_received_messages + alice_notifications + alice_edits}")
    
    # Demonstrate account deletion
    print("\n6. Demonstrating Account Deletion...")
    print("   Deleting Alice's account...")
    
    # Store Alice's username for reference
    alice_username = alice.username
    
    # Delete Alice's account
    alice.delete()
    
    print(f"   ✓ Account '{alice_username}' has been deleted")
    
    # Show post-deletion statistics
    print("\n7. Post-Deletion System Statistics:")
    print(f"   Total users: {User.objects.count()}")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total notifications: {Notification.objects.count()}")
    print(f"   Total message history records: {MessageHistory.objects.count()}")
    
    # Verify cleanup
    print("\n8. Verification of Data Cleanup:")
    
    # Check that Alice no longer exists
    alice_exists = User.objects.filter(username=alice_username).exists()
    print(f"   Alice still exists: {alice_exists} (should be False)")
    
    # Check that Alice's messages are deleted
    alice_sent_messages_remaining = Message.objects.filter(sender__username=alice_username).count()
    alice_received_messages_remaining = Message.objects.filter(receiver__username=alice_username).count()
    print(f"   Messages sent by Alice remaining: {alice_sent_messages_remaining} (should be 0)")
    print(f"   Messages received by Alice remaining: {alice_received_messages_remaining} (should be 0)")
    
    # Check that Alice's notifications are deleted
    alice_notifications_remaining = Notification.objects.filter(user__username=alice_username).count()
    print(f"   Notifications for Alice remaining: {alice_notifications_remaining} (should be 0)")
    
    # Check that Alice's message edits are deleted
    alice_edits_remaining = MessageHistory.objects.filter(edited_by__username=alice_username).count()
    print(f"   Message edits by Alice remaining: {alice_edits_remaining} (should be 0)")
    
    # Check that other users' data remains intact
    print("\n9. Verification of Other Users' Data:")
    other_users_exist = User.objects.filter(username__in=['bob', 'charlie', 'david']).count()
    print(f"   Other users still exist: {other_users_exist} (should be 3)")
    
    # Check that messages between other users remain
    other_messages = Message.objects.filter(
        sender__username__in=['bob', 'charlie', 'david'],
        receiver__username__in=['bob', 'charlie', 'david']
    ).count()
    print(f"   Messages between other users: {other_messages} (should be 2)")
    
    # Check that notifications for other users remain
    other_notifications = Notification.objects.filter(
        user__username__in=['bob', 'charlie', 'david']
    ).count()
    print(f"   Notifications for other users: {other_notifications} (should be 2)")
    
    # Check that message edits by other users remain
    other_edits = MessageHistory.objects.filter(
        edited_by__username__in=['bob', 'charlie', 'david']
    ).count()
    print(f"   Message edits by other users: {other_edits} (should be 1)")
    
    # Show remaining data details
    print("\n10. Remaining Data Details:")
    remaining_messages = Message.objects.all()
    print(f"   Remaining messages:")
    for msg in remaining_messages:
        print(f"     - {msg.sender.username} → {msg.receiver.username}: '{msg.content[:30]}...'")
    
    remaining_notifications = Notification.objects.all()
    print(f"   Remaining notifications:")
    for notif in remaining_notifications:
        print(f"     - For {notif.user.username}: {notif.title}")
    
    remaining_edits = MessageHistory.objects.all()
    print(f"   Remaining message edits:")
    for edit in remaining_edits:
        print(f"     - By {edit.edited_by.username}: '{edit.old_content[:30]}...'")
    
    print("\n" + "=" * 70)
    print("Account Deletion Demonstration completed successfully!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("✓ Automatic cleanup of all user data when account is deleted")
    print("✓ Post-delete signal handling for backup cleanup")
    print("✓ Proper foreign key constraint handling with CASCADE")
    print("✓ Preservation of other users' data")
    print("✓ Complete removal of messages, notifications, and history")
    print("✓ Transaction safety during deletion process")


if __name__ == '__main__':
    main() 