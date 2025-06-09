from rest_framework import serializers
from hairbnb.models import AIConversation, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    """
    S'occupe de la sérialisation d'un seul message.
    """
    class Meta:
        model = AIMessage
        fields = ['id', 'content', 'is_user', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AIConversationSerializer(serializers.ModelSerializer):
    """
    S'occupe de la sérialisation d'une conversation complète avec tous ses messages.
    """
    messages = AIMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIConversation
        fields = ['id', 'user_id', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']


class ConversationListSerializer(serializers.ModelSerializer):
    """
    S'occupe de la sérialisation d'un élément dans la liste des conversations (plus léger).
    """
    class Meta:
        model = AIConversation
        fields = ['id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateConversationResponseSerializer(serializers.ModelSerializer):
    """
    Formate la réponse lors de la création d'une nouvelle conversation.
    """
    conversation_id = serializers.IntegerField(source='id')

    class Meta:
        model = AIConversation
        fields = ['conversation_id', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']


class SendMessageRequestSerializer(serializers.Serializer):
    """
    Valide les données reçues lors de l'envoi d'un message.
    """
    conversation_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=True)


class SendMessageResponseSerializer(serializers.Serializer):
    """
    Formate la réponse envoyée au front-end après une question à l'IA.
    """
    conversation_id = serializers.IntegerField()
    user_message_id = serializers.IntegerField()
    ai_message_id = serializers.IntegerField()
    ai_response = serializers.CharField()