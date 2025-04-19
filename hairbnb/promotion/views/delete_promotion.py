# 📁 promotions/favorites_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from hairbnb.models import TblPromotion


@api_view(['DELETE'])
def delete_promotion(request, promotion_id):
    try:
        promotion = TblPromotion.objects.get(idPromotion=promotion_id)
        promotion.delete()
        return Response({'status': 'success', 'message': 'Promotion supprimée.'}, status=status.HTTP_204_NO_CONTENT)
    except TblPromotion.DoesNotExist:
        return Response({'status': 'error', 'message': 'Promotion introuvable.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
