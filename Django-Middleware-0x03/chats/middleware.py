from datetime import datetime
from rest_framework.response import Response
from django.http import JsonResponse
import os


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = os.path.join(os.path.dirname(__file__), 'requests.log')

    def __call__(self, request):
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the application based on time.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if 9 <= current_hour < 18:  # Allow access only between 9 AM and 6 PM
            return self.get_response(request)
        else:
            return Response({"detail": "Access restricted outside of business hours."}, status=403)
        
class OffensiveLanguageMiddleware :
    """
    Middleware to filter offensive language in requests and rate-limit messages per IP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to track message timestamps per IP
        self.ip_message_log = {}
        self.MESSAGE_LIMIT = 5
        self.TIME_WINDOW = 60  # seconds (1 minute)

    def __call__(self, request):
        if request.method == 'POST' and 'message' in getattr(request, 'data', {}):
            ip = self.get_client_ip(request)
            now = datetime.now().timestamp()
            # Initialize or clean up old timestamps
            timestamps = self.ip_message_log.get(ip, [])
            # Remove timestamps older than TIME_WINDOW
            timestamps = [ts for ts in timestamps if now - ts < self.TIME_WINDOW]
            if len(timestamps) >= self.MESSAGE_LIMIT:
                return Response({"detail": "Rate limit exceeded: Max 5 messages per minute."}, status=429)
            # Add current timestamp
            timestamps.append(now)
            self.ip_message_log[ip] = timestamps
            message = request.data['message']

        
        return self.get_response(request)

    def contains_offensive_language(self, message):
        # Placeholder for actual offensive language detection logic
        offensive_words = ['badword1', 'badword2']  # Example offensive words
        return any(word in message.lower() for word in offensive_words)

    def get_client_ip(self, request):
        # Try to get the real IP if behind a proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RolepermissionMiddleware:
    """
    Middleware to check user's role (admin/moderator) before allowing access to specific actions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected paths that require admin/moderator access
        self.protected_paths = [
            '/admin/',
            '/api/admin/',
            '/api/moderate/',
            '/api/users/',
            '/api/conversations/manage/',
        ]

    def __call__(self, request):
        # Check if the current path requires role-based access
        if self.is_protected_path(request.path):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    "detail": "Authentication required for this action."
                }, status=401)
            
            # Check if user has admin or moderator role
            if not self.has_admin_or_moderator_role(request.user):
                return JsonResponse({
                    "detail": "Access denied. Admin or moderator role required."
                }, status=403)
        
        return self.get_response(request)

    def is_protected_path(self, path):
        """
        Check if the current path requires role-based access.
        """
        return any(protected_path in path for protected_path in self.protected_paths)

    def has_admin_or_moderator_role(self, user):
        """
        Check if the user has admin or moderator role.
        """
        # Check if user is a superuser (admin)
        if user.is_superuser:
            return True
        
        # Check if user is staff
        if user.is_staff:
            return True
        
        # Check if user belongs to admin or moderator groups
        admin_groups = ['admin', 'moderator', 'administrator']
        user_groups = [group.name.lower() for group in user.groups.all()]
        
        return any(group in user_groups for group in admin_groups)

  