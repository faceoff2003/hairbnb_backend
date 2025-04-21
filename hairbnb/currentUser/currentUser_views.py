# **************************************************************************************************************************
from rest_framework.decorators import api_view
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.currentUser.CurrentUser_serializer import CurrentUserSerializer



@api_view(['GET'])
@firebase_authenticated
#@is_owner
def get_current_user(request):
    user = request.user

    if not user or not hasattr(user, 'uuid'):
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    serializer = CurrentUserSerializer(user)
    return Response({"status": "success", "user": serializer.data}, status=200)


# @api_view(['GET'])
# #@permission_classes([IsAuthenticated])
# def get_current_user(request):
#     """
#     API Endpoint pour récupérer les infos du current user Firebase.
#     """
#     user = request.user  # Injecté automatiquement par ta middleware Firebase
#
#     if not user or not hasattr(user, 'uuid'):
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
#
#     serializer = CurrentUserSerializer(user)
#     return Response({"status": "success", "user": serializer.data}, status=200)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Assure que l'utilisateur est connecté
# def get_current_user(request):
#     """
#     API Endpoint pour récupérer les informations du current user.
#     """
#     try:
#         user = TblUser.objects.get(uuid=request.tbluser.uuid)  # On récupère l'utilisateur via son UUID Firebase
#         serializer = CurrentUserSerializer(user)
#         return Response({"status": "success", "user": serializer.data}, status=200)
#     except TblUser.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
# **************************************************************************************************************************