from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decorators.decorators import firebase_authenticated, is_admin
from hairbnb.models import TblUser, TblRole
from .admin_serializers import AdminUserActionSerializer, AdminUserListSerializer


@api_view(['GET'])
@firebase_authenticated
@is_admin
def list_users(request):
    """Liste tous les utilisateurs pour l'admin"""
    users = TblUser.objects.all().order_by('-idTblUser')
    serializer = AdminUserListSerializer(users, many=True)
    return Response({
        'success': True,
        'users': serializer.data
    })


@api_view(['POST'])
@firebase_authenticated
@is_admin
def manage_user(request):
    """Gérer un utilisateur (activer/désactiver/changer rôle)"""
    global action_message
    serializer = AdminUserActionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = get_object_or_404(TblUser, idTblUser=data['user_id'])

    # Empêcher l'admin de se désactiver lui-même
    if user.idTblUser == request.admin_user.idTblUser and data['action'] == 'deactivate':
        return Response({
            'success': False,
            'message': 'Impossible de se désactiver soi-même'
        }, status=status.HTTP_400_BAD_REQUEST)

    if data['action'] == 'deactivate':
        user.is_active = False
        action_message = f"Utilisateur {user.prenom} {user.nom} désactivé"

    elif data['action'] == 'activate':
        user.is_active = True
        action_message = f"Utilisateur {user.prenom} {user.nom} activé"

    elif data['action'] == 'change_role':
        new_role = get_object_or_404(TblRole, idTblRole=data['new_role_id'])
        old_role = user.get_role()
        user.role = new_role
        action_message = f"Rôle de {user.prenom} {user.nom} changé de {old_role} vers {new_role.nom}"

    user.save()

    return Response({
        'success': True,
        'message': action_message
    })