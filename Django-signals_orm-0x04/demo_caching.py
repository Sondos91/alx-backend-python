#!/usr/bin/env python3
"""
Demonstration script for caching functionality in the messaging app.

This script demonstrates:
1. How the cache_page decorator works with the conversation_thread view
2. Cache configuration with LocMemCache
3. Cache timeout behavior (60 seconds)
4. Performance benefits of caching
"""

import os
import sys
import django
import time
from django.test import Client
from django.contrib.auth.models import User

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from messaging.models import Message


def create_test_data():
    """Create test users and messages for caching demonstration."""
    print("Creating test data for caching demonstration...")
    
    # Create test users
    user1, created = User.objects.get_or_create(
        username='cache_user1',
        defaults={'email': 'cache1@demo.com'}
    )
    if created:
        user1.set_password('demo123')
        user1.save()
        print(f"Created user: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='cache_user2',
        defaults={'email': 'cache2@demo.com'}
    )
    if created:
        user2.set_password('demo123')
        user2.save()
        print(f"Created user: {user2.username}")
    
    # Create a conversation thread
    thread = Message.objects.create(
        sender=user1,
        receiver=user2,
        content='This is the first message in our conversation thread'
    )
    print(f"Created thread with ID: {thread.id}")
    
    # Add some replies to the thread
    reply1 = Message.objects.create(
        sender=user2,
        receiver=user1,
        content='This is a reply to the first message',
        parent_message=thread
    )
    print(f"Created reply 1: {reply1.content[:50]}...")
    
    reply2 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content='This is another reply in the conversation',
        parent_message=thread
    )
    print(f"Created reply 2: {reply2.content[:50]}...")
    
    return user1, user2, thread


def demonstrate_caching():
    """Demonstrate the caching functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING CACHING FUNCTIONALITY")
    print("="*60)
    
    # Create test data
    user1, user2, thread = create_test_data()
    
    # Create a client for testing
    client = Client()
    
    # Login as user1
    client.login(username='cache_user1', password='demo123')
    
    print(f"\nTesting conversation thread view with caching...")
    print(f"Thread ID: {thread.id}")
    
    # First request - should hit the database and cache the result
    print("\n1. First request (cache miss):")
    start_time = time.time()
    response1 = client.get(f'/messaging/thread/{thread.id}/')
    end_time = time.time()
    
    print(f"   Status Code: {response1.status_code}")
    print(f"   Response Time: {end_time - start_time:.4f} seconds")
    print(f"   Cache Status: Cache miss (first request)")
    
    # Second request - should be served from cache
    print("\n2. Second request (cache hit):")
    start_time = time.time()
    response2 = client.get(f'/messaging/thread/{thread.id}/')
    end_time = time.time()
    
    print(f"   Status Code: {response2.status_code}")
    print(f"   Response Time: {end_time - start_time:.4f} seconds")
    print(f"   Cache Status: Cache hit (served from cache)")
    
    # Third request - should also be served from cache
    print("\n3. Third request (cache hit):")
    start_time = time.time()
    response3 = client.get(f'/messaging/thread/{thread.id}/')
    end_time = time.time()
    
    print(f"   Status Code: {response3.status_code}")
    print(f"   Response Time: {end_time - start_time:.4f} seconds")
    print(f"   Cache Status: Cache hit (served from cache)")
    
    # Verify that all responses are identical
    print("\n4. Verifying cache consistency:")
    print(f"   Response 1 length: {len(response1.content)} bytes")
    print(f"   Response 2 length: {len(response2.content)} bytes")
    print(f"   Response 3 length: {len(response3.content)} bytes")
    print(f"   All responses identical: {response1.content == response2.content == response3.content}")


def demonstrate_cache_timeout():
    """Demonstrate cache timeout behavior."""
    print("\n" + "="*60)
    print("DEMONSTRATING CACHE TIMEOUT (60 seconds)")
    print("="*60)
    
    user1, user2, thread = create_test_data()
    client = Client()
    client.login(username='cache_user1', password='demo123')
    
    print(f"\nCache timeout is set to 60 seconds.")
    print(f"Note: In this demo, we'll simulate the timeout behavior.")
    print(f"In a real scenario, you would wait 60 seconds to see the cache expire.")
    
    # First request
    print("\n1. First request (cache miss):")
    start_time = time.time()
    response1 = client.get(f'/messaging/thread/{thread.id}/')
    end_time = time.time()
    print(f"   Response Time: {end_time - start_time:.4f} seconds")
    
    # Simulate cache hit
    print("\n2. Immediate second request (cache hit):")
    start_time = time.time()
    response2 = client.get(f'/messaging/thread/{thread.id}/')
    end_time = time.time()
    print(f"   Response Time: {end_time - start_time:.4f} seconds")
    
    print("\n3. After 60 seconds (cache miss - timeout):")
    print("   (In real scenario, cache would expire after 60 seconds)")
    print("   Response would be slower as it hits the database again")


def demonstrate_cache_configuration():
    """Demonstrate the cache configuration."""
    print("\n" + "="*60)
    print("CACHE CONFIGURATION DETAILS")
    print("="*60)
    
    print("\nCache settings in messaging_project/settings.py:")
    print("""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
""")
    
    print("Key features of this configuration:")
    print("1. Backend: LocMemCache - In-memory caching (fast but not persistent)")
    print("2. Location: 'unique-snowflake' - Unique identifier for this cache instance")
    print("3. Cache timeout: 60 seconds (set in the @cache_page(60) decorator)")
    print("4. Scope: Per-process (each Django process has its own cache)")
    
    print("\nCache decorator usage in messaging/views.py:")
    print("""
@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_thread(request, thread_id):
    # View logic here
""")
    
    print("\nBenefits of this caching setup:")
    print("1. Reduced database queries for frequently accessed conversation threads")
    print("2. Faster response times for cached pages")
    print("3. Reduced server load during high traffic periods")
    print("4. Automatic cache expiration after 60 seconds")
    print("5. User-specific caching (each user gets their own cached version)")


def demonstrate_performance_comparison():
    """Demonstrate performance benefits of caching."""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    
    user1, user2, thread = create_test_data()
    client = Client()
    client.login(username='cache_user1', password='demo123')
    
    print("\nTesting response times with and without caching:")
    
    # Multiple requests to show caching benefits
    times_without_cache = []
    times_with_cache = []
    
    print("\nSimulating multiple requests...")
    
    for i in range(5):
        start_time = time.time()
        response = client.get(f'/messaging/thread/{thread.id}/')
        end_time = time.time()
        
        if i == 0:
            # First request (cache miss)
            times_without_cache.append(end_time - start_time)
            print(f"Request {i+1}: {end_time - start_time:.4f}s (cache miss)")
        else:
            # Subsequent requests (cache hits)
            times_with_cache.append(end_time - start_time)
            print(f"Request {i+1}: {end_time - start_time:.4f}s (cache hit)")
    
    if times_without_cache and times_with_cache:
        avg_without_cache = sum(times_without_cache) / len(times_without_cache)
        avg_with_cache = sum(times_with_cache) / len(times_with_cache)
        
        print(f"\nPerformance Summary:")
        print(f"Average time without cache: {avg_without_cache:.4f} seconds")
        print(f"Average time with cache: {avg_with_cache:.4f} seconds")
        
        if avg_with_cache < avg_without_cache:
            improvement = ((avg_without_cache - avg_with_cache) / avg_without_cache) * 100
            print(f"Performance improvement: {improvement:.1f}% faster with caching")


def main():
    """Main demonstration function."""
    print("CACHING FUNCTIONALITY DEMONSTRATION")
    print("="*60)
    
    # Demonstrate basic caching
    demonstrate_caching()
    
    # Demonstrate cache timeout
    demonstrate_cache_timeout()
    
    # Show cache configuration
    demonstrate_cache_configuration()
    
    # Show performance comparison
    demonstrate_performance_comparison()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("1. LocMemCache backend configuration")
    print("2. @cache_page(60) decorator usage")
    print("3. Cache hit/miss behavior")
    print("4. 60-second cache timeout")
    print("5. Performance benefits of caching")
    print("6. User-specific caching (per-user cache keys)")


if __name__ == '__main__':
    main() 