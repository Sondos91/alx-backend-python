from rest_framework .permissions import  BasePermission

class IsParticipantofConversation(BasePermission):
    """
    Custom permission to check if the user is a participant of the conversation for PUT, PATCH, and DELETE requests.
    """
    def has_permission(self, request, view):
        if request.method not in ["PUT", "PATCH", "DELETE"]:
            return True  # Allow other methods
        conversation_id = view.kwargs.get('pk')
        if not conversation_id:
            return False
        user = request.user
        return user.is_authenticated and user.conversations.filter(conversation_id=conversation_id).exists()