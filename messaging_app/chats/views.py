from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Conversation, Message, user
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantofConversation
from .auth import CustomAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.



class ConversationFilter(filters.FilterSet):
    created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    participant = filters.CharFilter(field_name='participants__username', lookup_expr='icontains')
    
    class Meta:
        model = Conversation
        fields = ['created_at', 'participant']


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filterset_class = ConversationFilter

    def get_queryset(self):
        user_id = self.request.user.user_id
        return self.queryset.filter(participants__user_id=user_id)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save()
        return Response({'status': 'conversation archived'}, status=status.HTTP_200_OK)


class MessageFilter(filters.FilterSet):
    sent_at = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sender = filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    
    class Meta:
        model = Message
        fields = ['sent_at', 'sender']


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filterset_class = MessageFilter
    permission_classes = [IsAuthenticated, IsParticipantofConversation]

    def get_queryset(self):
        user_id = self.request.user.user_id
        conversation_id = self.kwargs.get('conversation_id')
        # Explicitly use Message.objects.filter
        return Message.objects.filter(
            conversation__conversation_id=conversation_id,
            conversation__participants__user_id=user_id)
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
        
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        # Example permission check using HTTP_403_FORBIDDEN
        if message.conversation not in self.request.user.conversations.all():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'}, status=status.HTTP_200_OK)