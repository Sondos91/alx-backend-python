from rest_framework import permissions,BasePermission
from rest_framework .decorators import action

class IsParticipantofConversation(BasePermission):
    """
    Custom permission to check if the user is a participant of the conversation.
    """
    @action(detail=True, methods=['post','put','delete'])
    def has_permission(self, request, view):    
        conversation_id=view.kwargs.get('pk')
        if not conversation_id:
            return False
        
        user = request.user
        return user.is_authenticated and user.conversations.filter(conversation_id=conversation_id).exists()