from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for a single chat message."""
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for a chat session, including all its messages."""
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'topic', 'messages', 'created_at']
        read_only_fields = ['user']

class MessageInputSerializer(serializers.Serializer):
    """Serializer for the user's input when sending a message."""
    prompt = serializers.CharField(max_length=4000)