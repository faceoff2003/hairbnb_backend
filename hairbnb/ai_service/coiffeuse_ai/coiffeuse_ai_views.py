# hairbnb/ai_service/coiffeuse_ai_views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Imports des décorateurs et des modèles/services nécessaires
from decorators.decorators import firebase_authenticated, is_owner_coiffeuse
from hairbnb.ai_service.ai_service import AIService
from hairbnb.ai_service.coiffeuse_ai.coiffeuse_ai_serializers import AIConversationSerializer, \
    SendMessageRequestSerializer
from hairbnb.ai_service.utils import get_database_context_for_query
from hairbnb.models import AIConversation, AIMessage


# --- VUES POUR LA GESTION DES CONVERSATIONS ---

@api_view(['GET'])
@firebase_authenticated
@is_owner_coiffeuse
def get_coiffeuse_conversations(request):
    """Récupère la liste des conversations pour la coiffeuse propriétaire connectée."""
    conversations = AIConversation.objects.filter(user=request.user).order_by('-created_at')

    # On construit la réponse manuellement pour ajouter des détails utiles
    data = []
    for conv in conversations:
        last_message = conv.messages.last()
        data.append({
            'id': conv.id,
            'created_at': conv.created_at,
            'tokens_used': conv.tokens_used,
            'title': last_message.content[:50] + '...' if last_message else 'Nouvelle Conversation'
        })
    return Response(data)


@api_view(['POST'])
@firebase_authenticated
@is_owner_coiffeuse
def create_coiffeuse_conversation(request):
    """Crée une nouvelle conversation pour la coiffeuse propriétaire."""
    conversation = AIConversation.objects.create(user=request.user)
    return Response({'id': conversation.id, 'created_at': conversation.created_at}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@firebase_authenticated
@is_owner_coiffeuse
def get_coiffeuse_conversation_messages(request, conversation_id):
    """Récupère les messages d'une conversation spécifique, en vérifiant que la coiffeuse en est propriétaire."""
    conversation = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
    serializer = AIConversationSerializer(conversation)
    return Response(serializer.data)


@api_view(['DELETE'])
@firebase_authenticated
@is_owner_coiffeuse
def delete_coiffeuse_conversation(request, conversation_id):
    """Supprime une conversation et ses messages pour la coiffeuse propriétaire."""
    conversation = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
    conversation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --- VUE PRINCIPALE POUR L'INTERACTION AVEC L'IA ---

@api_view(['POST'])
@firebase_authenticated
@is_owner_coiffeuse
def send_coiffeuse_message(request):
    """
    Le point d'entrée principal. Reçoit un message d'une coiffeuse propriétaire,
    récupère le contexte de ses données, interroge l'IA et renvoie la réponse.
    """
    # 1. Valider la requête
    request_serializer = SendMessageRequestSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = request_serializer.validated_data
    message_content = validated_data['message']
    conversation_id = validated_data.get('conversation_id')

    # 2. Gérer la conversation
    if conversation_id:
        # Sécurité : on vérifie que la conversation appartient bien à l'utilisateur
        conversation = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
    else:
        conversation = AIConversation.objects.create(user=request.user)

    # 3. Sauvegarder le message de l'utilisateur
    user_message = AIMessage.objects.create(
        conversation=conversation,
        content=message_content,
        is_user=True
    )

    # 4. Préparer le contexte pour l'IA
    message_history = []
    recent_messages = conversation.messages.filter(id__lt=user_message.id).order_by('-timestamp')[:4]
    for msg in reversed(list(recent_messages)):
        message_history.append({"role": "user" if msg.is_user else "assistant", "content": msg.content})

    # ✅ APPEL À L'UTILITAIRE SÉCURISÉ
    db_context = get_database_context_for_query(message_content, request.user)

    # 5. Appeler le service IA (le service lui-même est générique et n'a pas besoin de changer)
    ai_service = AIService()
    ai_result = ai_service.get_response(
        query=message_content,
        context=db_context,
        message_history=message_history
    )

    ai_response = ai_result["response"]
    tokens_data = ai_result.get("tokens", {})

    # 6. Sauvegarder la réponse de l'IA et mettre à jour les tokens
    AIMessage.objects.create(
        conversation=conversation,
        content=ai_response,
        is_user=False,
        tokens_in=tokens_data.get("input", 0),
        tokens_out=tokens_data.get("output", 0)
    )
    conversation.tokens_used += tokens_data.get("total", 0)
    conversation.save()

    # 7. Renvoyer la réponse à l'application
    return Response({
        'conversation_id': conversation.id,
        'ai_response': ai_response,
        'tokens': tokens_data
    })