from datetime import datetime
from rest_framework.response import Response


class RequestLoggingMiddleware :
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        user=request.user if request.user.is_authenticated else None
        print(f"{datetime.now()} - User: {user} - Path: {request.path}")
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

  