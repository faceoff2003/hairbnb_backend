import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .views import logger
from ..business.business_logic import MinimalCoiffeuseData
from ..currentUser.CurrentUser_serializer import CurrentUserSerializer
from ..models import TblCoiffeuse, TblClient, TblUser, TblSalon
from ..serializers.users_serializers import CoiffeuseSerializer, ClientSerializer


#*****************************************Afficher la coiffeuse****************************************
@api_view(['GET'])
def get_coiffeuse_by_uuid(request, uuid):
    try:
        user = TblUser.objects.get(uuid=uuid, type='coiffeuse')
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
        serializer = CoiffeuseSerializer(coiffeuse)

        return Response({"status": "success", "data": serializer.data}, status=200)

    except TblUser.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur introuvable ou non une coiffeuse."}, status=404)

    except TblCoiffeuse.DoesNotExist:
        return Response({"status": "error", "message": "Coiffeuse introuvable."}, status=404)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
#**************************************************************************************************************************

#*************************************************Afficher le client*******************************************************

@api_view(['GET'])
def get_client_by_uuid(request, uuid):
    try:
        user = TblUser.objects.get(uuid=uuid, type='client')
        client = TblClient.objects.get(idTblUser=user)
        serializer = ClientSerializer(client)

        return Response({"status": "success", "data": serializer.data}, status=200)

    except TblUser.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur introuvable ou non un client."}, status=404)

    except TblClient.DoesNotExist:
        return Response({"status": "error", "message": "Client introuvable."}, status=404)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

# **************************************************************************************************************************

# ********************************************update_coiffeuse**********************************************************
@api_view(['PUT'])
def update_coiffeuse(request, uuid):
    try:
        coiffeuse = TblCoiffeuse.objects.get(uuid=uuid)
    except TblCoiffeuse.DoesNotExist:
        return Response({'error': 'Coiffeuse not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CoiffeuseSerializer(coiffeuse, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# **************************************************************************************************************************

# ********************************************update_client**********************************************************
@api_view(['PUT'])
def update_client(request, uuid):
    try:
        client = TblClient.objects.get(uuid=uuid)
    except TblClient.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClientSerializer(client, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# **************************************************************************************************************************

# **************************************************************************************************************************
                       #get_current_user (Assure que l'utilisateur est connecté et renvoi le current user)
# # **************************************************************************************************************************
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
# # **************************************************************************************************************************

# **************************************************************************************************************************
                            #get_current_user (Reçoi le uuid et renvoi le current user)
# **************************************************************************************************************************
@api_view(['GET'])
def get_current_user(request, uuid):
    """
    API Endpoint pour récupérer les informations d'un utilisateur via son UUID.
    """
    try:
        user = TblUser.objects.get(uuid=uuid)  # Recherche de l'utilisateur par UUID
        serializer = CurrentUserSerializer(user)
        return Response({"status": "success", "user": serializer.data}, status=200)
    except ObjectDoesNotExist:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
# **************************************************************************************************************************
# **************************************************************************************************************************
                            #get_coiffeuses_info
# **************************************************************************************************************************
@api_view(['POST'])
def get_coiffeuses_info(request):
    try:
        data = json.loads(request.body)
        uuids = data.get("uuids", [])

        logger.info(f"📩 UUIDs reçus : {uuids}")  # ✅ Log des UUIDs reçus

        # ✅ Récupérer les coiffeuses qui correspondent aux UUIDs
        coiffeuses = TblCoiffeuse.objects.filter(idTblUser__uuid__in=uuids)

        # ✅ Transformer les objets en JSON minimaliste
        coiffeuses_data = [MinimalCoiffeuseData(c).to_dict() for c in coiffeuses]

        logger.info(f"🔍 Coiffeuses trouvées : {coiffeuses_data}")  # ✅ Log des données retournées

        return JsonResponse({"status": "success", "coiffeuses": coiffeuses_data})

    except Exception as e:
        logger.error(f"❌ Erreur interne : {str(e)}", exc_info=True)
        return JsonResponse({"status": "error", "message": "Erreur interne"}, status=500)


# @api_view(['GET'])
# def get_salon_by_coiffeuse(request, coiffeuse_id):
#     """
#     Récupère le salon associé à une coiffeuse.
#     """
#     try:
#         salon = TblSalon.objects.get(coiffeuse__idTblUser=coiffeuse_id)
#         return Response({"idSalon": salon.idTblSalon})
#     except TblSalon.DoesNotExist:
#         return Response({"error": "Salon introuvable"}, status=404)





