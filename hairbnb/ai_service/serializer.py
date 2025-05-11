# hairbnb/claud_ai/serializers.py
from rest_framework import serializers
from hairbnb.models import AIConversation, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'content', 'is_user', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIConversation
        fields = ['id', 'user_id', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']


class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ['id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateConversationResponseSerializer(serializers.ModelSerializer):
    conversation_id = serializers.IntegerField(source='id')

    class Meta:
        model = AIConversation
        fields = ['conversation_id', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']


class SendMessageRequestSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=True)


class SendMessageResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    user_message_id = serializers.IntegerField()
    ai_message_id = serializers.IntegerField()
    ai_response = serializers.CharField()