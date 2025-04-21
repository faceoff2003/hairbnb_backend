from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from hairbnb.favorites.favorites_serializer import TblFavoriteSerializer
from hairbnb.models import TblFavorite, TblSalon, TblUser
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def get_favorites(request):
    user_id = request.GET.get('user')  # 🔄 Exemple : ?user=5
    if not user_id:
        return Response({"error": "Paramètre 'user' requis"}, status=status.HTTP_400_BAD_REQUEST)

    favorites = TblFavorite.objects.filter(user__idTblUser=user_id)
    serializer = TblFavoriteSerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_favorites(request):
    """
    🔍 Vue qui retourne la liste des salons ajoutés en favoris par un utilisateur donné.

    📥 Paramètre attendu dans l'URL :
        - user (int) : ID de l'utilisateur (idTblUser)
          Exemple : /api/favorites/?user=2

    🔁 Traitement :
        - Filtre les enregistrements dans TblFavorite où l'utilisateur correspond.
        - Sérialise chaque favori en incluant les détails du salon (si le serializer est configuré ainsi).

    📤 Rendu :
        - Type : JSON
        - Structure : Liste d'objets contenant les infos du favori
          Exemple :
          [
              {
                  "idTblFavorite": 1,
                  "salon": {
                      "idTblSalon": 3,
                      "nom_salon": "Salon Chic",
                      "slogan": "Beauté moderne",
                      "logo_salon": "https://.../logo.jpg",
                      ...
                  },
                  "added_at": "2025-04-18T09:00:00Z"
              },
              ...
          ]
    """
    user_id = request.GET.get('user')  # Ex: /api/favorites/?user=2

    if not user_id:
        return Response({"error": "Paramètre 'user' requis"}, status=status.HTTP_400_BAD_REQUEST)

    favorites = TblFavorite.objects.filter(user__idTblUser=user_id).select_related('salon')
    serializer = TblFavoriteSerializer(favorites, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def add_favorite(request):
    user_id = request.data.get("user")
    salon_id = request.data.get("salon")

    if not user_id or not salon_id:
        return Response({"error": "Champs 'user' et 'salon' requis"}, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier que l'utilisateur et le salon existent
    user = get_object_or_404(TblUser, idTblUser=user_id)
    salon = get_object_or_404(TblSalon, idTblSalon=salon_id)

    favorite, created = TblFavorite.objects.get_or_create(user=user, salon=salon)
    serializer = TblFavoriteSerializer(favorite)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['DELETE'])
def remove_favorite(request):
    favorite_id = request.data.get("id")

    if not favorite_id:
        return Response({"error": "Le champ 'id' est requis"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        favorite = TblFavorite.objects.get(idTblFavorite=favorite_id)
        favorite.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
    except TblFavorite.DoesNotExist:
        return Response({"error": "Favori non trouvé"}, status=status.HTTP_404_NOT_FOUND)




# @api_view(['DELETE'])
# def remove_favorite(request):
#     user_id = request.data.get("user")
#     salon_id = request.data.get("salon")
#
#     if not user_id or not salon_id:
#         return Response({"error": "Champs 'user' et 'salon' requis"}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         favorite = TblFavorite.objects.get(user__idTblUser=user_id, salon__idTblSalon=salon_id)
#         favorite.delete()
#         return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
#     except TblFavorite.DoesNotExist:
#         return Response({"error": "Favori non trouvé"}, status=status.HTTP_404_NOT_FOUND)
