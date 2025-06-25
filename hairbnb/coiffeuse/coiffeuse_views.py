import json
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated, is_owner_coiffeuse
from hairbnb.coiffeuse.coiffeuse_business_logic import MinimalCoiffeuseData
from hairbnb.coiffeuse.coiffeuse_serializers import UpdateNomCommercialSerializer
from hairbnb.models import TblCoiffeuse, TblUser

logger = logging.getLogger(__name__)
@api_view(['POST'])
def get_coiffeuses_info(request):
    """
    Récupère les informations des coiffeuses à partir d'une liste d'UUIDs.

    Requête attendue:
    {
        "uuids": ["uuid1", "uuid2", ...]
    }
    """
    try:
        # Récupérer et valider les données de la requête
        data = json.loads(request.body)
        uuids = data.get("uuids", [])

        if not uuids:
            return JsonResponse({
                "status": "error",
                "message": "Aucun UUID fourni"
            }, status=400)

        logger.info(f"📩 UUIDs reçus : {uuids}")

        # Récupérer les coiffeuses qui correspondent aux UUIDs
        coiffeuses = TblCoiffeuse.objects.filter(idTblUser__uuid__in=uuids)

        # Transformer les objets en JSON minimaliste
        coiffeuses_data = [MinimalCoiffeuseData(c).to_dict() for c in coiffeuses]

        # Log un résumé des résultats (nombre de coiffeuses trouvées)
        logger.info(f"🔍 {len(coiffeuses_data)} coiffeuses trouvées sur {len(uuids)} UUIDs demandés")

        return JsonResponse({
            "status": "success",
            "coiffeuses": coiffeuses_data
        })

    except json.JSONDecodeError:
        logger.error("❌ Format JSON invalide dans la requête")
        return JsonResponse({
            "status": "error",
            "message": "Format de requête invalide"
        }, status=400)

    except Exception as e:
        # Log l'erreur complète avec la stack trace
        logger.error(f"❌ Erreur interne : {str(e)}", exc_info=True)

        return JsonResponse({
            "status": "error",
            "message": "Erreur interne du serveur"
        }, status=500)


@api_view(['PATCH'])
@firebase_authenticated
@is_owner_coiffeuse
def update_coiffeuse_nom_commercial(request, uuid):
    """
    Met à jour le nom commercial d'une coiffeuse propriétaire
    """
    try:
        # Récupérer l'utilisateur par UUID
        user = get_object_or_404(TblUser, uuid=uuid)

        # Vérifier que c'est le bon utilisateur (sécurité)
        if user != request.user:
            return Response({
                "success": False,
                "message": "Vous ne pouvez modifier que votre propre profil"
            }, status=status.HTTP_403_FORBIDDEN)

        # Utiliser le serializer
        serializer = UpdateNomCommercialSerializer(
            user.coiffeuse,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Nom commercial mis à jour avec succès",
                "data": {
                    "nom_commercial": serializer.validated_data['nom_commercial']
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "message": f"Erreur: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)