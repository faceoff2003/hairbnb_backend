import json
import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view
from hairbnb.coiffeuse.coiffeuse_business_logic import MinimalCoiffeuseData
from hairbnb.models import TblCoiffeuse

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