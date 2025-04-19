from hairbnb.models import TblService, TblPromotion
from hairbnb.promotion.business_logique import PromotionManager
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_promotions_for_service(request, service_id):
    try:
        service = TblService.objects.get(idTblService=service_id)
        promo_mgr = PromotionManager(service)

        # Récupérer pagination depuis la query string
        try:
            page = int(request.GET.get("page") or 1)
        except ValueError:
            page = 1

        try:
            page_size = int(request.GET.get("page_size") or 5)
        except ValueError:
            page_size = 5

        # S'il demande les expirées
        expired_data = {}
        if request.GET.get("expired"):
            expired_data = promo_mgr.get_expired(page=page, page_size=page_size)

        return Response({
            "status": "success",
            "counts": promo_mgr.get_counts(),
            "active": promo_mgr.get_active(),
            "upcoming": promo_mgr.get_upcoming(),
            "expired": expired_data
        })

    except TblService.DoesNotExist:
        return Response({"status": "error", "message": "Service introuvable"}, status=404)

