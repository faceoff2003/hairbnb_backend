from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hairbnb.models import TblFavorite, TblSalon

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_favorites(request):
    favorites = TblFavorite.objects.filter(user=request.user)
    data = [{"salon_id": fav.salon.idTblSalon} for fav in favorites]
    return Response(data)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def add_favorite(request):
    salon_id = request.data.get("salon_id")
    if not salon_id:
        return Response({"error": "salon_id manquant"}, status=400)

    salon = TblSalon.objects.get(idTblSalon=salon_id)
    favorite, created = TblFavorite.objects.get_or_create(user=request.user, salon=salon)

    return Response({"success": True, "created": created})

@api_view(['DELETE'])
#@permission_classes([IsAuthenticated])
def remove_favorite(request, salon_id):
    deleted, _ = TblFavorite.objects.filter(user=request.user, salon_id=salon_id).delete()
    return Response({"success": deleted > 0})
