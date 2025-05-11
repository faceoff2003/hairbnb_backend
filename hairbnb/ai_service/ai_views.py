# hairbnb/ai_service/ai_views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decorators.decorators import firebase_authenticated
from .ai_service import AIService
from .utils import get_database_context_for_query
from ..models import AIConversation, AIMessage


# Vue pour récupérer toutes les conversations d'un utilisateur
@api_view(['GET'])
@firebase_authenticated
def get_conversations(request):
    try:
        # Récupérer l'utilisateur connecté
        user = request.user

        # Récupérer toutes les conversations de l'utilisateur
        conversations = AIConversation.objects.filter(user=user).order_by('-created_at')

        # Préparer les données pour la réponse
        conversations_data = [{
            'id': conv.id,
            'created_at': conv.created_at.isoformat(),
            'tokens_used': conv.tokens_used,
            'last_message': conv.messages.last().content[:100] if conv.messages.exists() else None
        } for conv in conversations]

        return Response({'conversations': conversations_data})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour récupérer les messages d'une conversation spécifique
@api_view(['GET'])
@firebase_authenticated
def get_conversation_messages(request, conversation_id):
    try:
        # Récupérer l'utilisateur connecté
        user = request.user

        # Récupérer la conversation spécifiée
        conversation = get_object_or_404(AIConversation, id=conversation_id, user=user)

        # Récupérer tous les messages de la conversation
        messages = conversation.messages.all().order_by('timestamp')

        # Préparer les données pour la réponse
        messages_data = [{
            'id': msg.id,
            'content': msg.content,
            'is_user': msg.is_user,
            'timestamp': msg.timestamp.isoformat(),
            'tokens_in': msg.tokens_in,
            'tokens_out': msg.tokens_out
        } for msg in messages]

        return Response({
            'conversation_id': conversation.id,
            'created_at': conversation.created_at.isoformat(),
            'tokens_used': conversation.tokens_used,
            'messages': messages_data
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour créer une nouvelle conversation
@api_view(['POST'])
@firebase_authenticated
def create_conversation(request):
    try:
        # Récupérer l'utilisateur connecté
        user = request.user

        # Créer une nouvelle conversation
        conversation = AIConversation.objects.create(
            user=user,
            context_cache={},  # Initialiser avec un objet vide
            tokens_used=0
        )

        return Response({
            'conversation_id': conversation.id,
            'created_at': conversation.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour envoyer un message et obtenir une réponse
@api_view(['POST'])
@firebase_authenticated
def send_message(request):
    try:
        # Extraire les données de la requête
        data = request.data
        conversation_id = data.get('conversation_id')
        message_content = data.get('message')

        if not message_content:
            return Response({'error': 'Le message est requis'}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer l'utilisateur connecté
        user = request.user

        # Récupérer ou créer la conversation
        if conversation_id:
            conversation = get_object_or_404(AIConversation, id=conversation_id, user=user)
        else:
            conversation = AIConversation.objects.create(
                user=user,
                context_cache={},
                tokens_used=0
            )

        # Initialiser le service IA
        ai_service = AIService()

        # Enregistrer le message de l'utilisateur
        tokens_in = ai_service.count_tokens(message_content)
        user_message = AIMessage.objects.create(
            conversation=conversation,
            content=message_content,
            is_user=True,
            tokens_in=tokens_in,
            tokens_out=0
        )

        # Récupérer l'historique des messages pour le contexte
        message_history = []
        # Limiter à quelques messages récents pour économiser des tokens
        recent_messages = conversation.messages.filter(id__lt=user_message.id).order_by('-timestamp')[:4]
        for msg in reversed(list(recent_messages)):
            role = "user" if msg.is_user else "assistant"
            message_history.append({"role": role, "content": msg.content})

        # Extraire le contexte de la base de données en fonction de la requête
        db_context = get_database_context_for_query(message_content)

        # Obtenir une réponse de l'IA
        ai_result = ai_service.get_response(
            query=message_content,
            context=db_context,
            message_history=message_history
        )

        # Extraire la réponse et les statistiques de tokens
        ai_response = ai_result["response"]
        tokens_data = ai_result.get("tokens", {"input": tokens_in, "output": 0, "total": tokens_in})

        # Enregistrer la réponse de l'IA
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False,
            tokens_in=0,
            tokens_out=tokens_data["output"]
        )

        # Mettre à jour le nombre total de tokens pour la conversation
        conversation.tokens_used += tokens_data["total"]
        conversation.save()

        # Renvoyer la réponse
        return Response({
            'conversation_id': conversation.id,
            'user_message_id': user_message.id,
            'ai_message_id': ai_message.id,
            'ai_response': ai_response,
            'tokens': tokens_data
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@firebase_authenticated
def delete_conversation(request, conversation_id):
    try:
        # Récupérer l'utilisateur connecté
        user = request.user

        # Récupérer la conversation spécifiée
        conversation = get_object_or_404(AIConversation, id=conversation_id, user=user)

        # Supprimer les messages associés à la conversation
        conversation.messages.all().delete()

        # Supprimer la conversation
        conversation.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT)  # 204 No Content est le code standard pour une suppression réussie

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)