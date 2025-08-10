from .models import Conversation, Message
from .models import CustomUser
from rest_framework import serializers
from rest_framework.serializers import CharField, SerializerMethodField
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone_number']
        read_only_fields = ['user_id']

class MessageSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField(max_length=1000)
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'conversation', 'sender', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    
    def get_message(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'created_at', 'participants', 'message']
        read_only_fields = ['conversation_id', 'created_at']
        
    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        for participant in participants_data:
            try:
                user_instance = CustomUser.objects.get(user_id=participant.user_id)
                conversation.participants.add(user_instance)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(f"User with ID {participant.user_id} does not exist")
        return conversation
        
