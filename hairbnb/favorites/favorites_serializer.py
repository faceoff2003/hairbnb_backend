# hairbnb/serializers/favorites_serializers.py
from rest_framework import serializers
from hairbnb.models import TblFavorite
from hairbnb.salon.salon_serializers import TblSalonSerializer


class TblFavoriteSerializer(serializers.ModelSerializer):
    # Conserver l'objet salon complet pour les endpoints existants
    salon = TblSalonSerializer(read_only=True)

    # Ajouter explicitement le champ user pour le rendre compatible avec le modèle Flutter
    user = serializers.IntegerField(source='user.idTblUser', read_only=True)

    # Ajouter le champ added_at pour correspondre au modèle Flutter
    #added_at = serializers.DateTimeField(source='added_at', read_only=True, format='%Y-%m-%dT%H:%M:%S')
    added_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = TblFavorite
        fields = ['idTblFavorite', 'user', 'salon', 'added_at']


# Nouveau serializer spécifique pour l'endpoint de vérification de favoris
class FavoriteCheckSerializer(serializers.ModelSerializer):
    # Pour ce serializer, on transforme le salon en ID entier
    salon = serializers.IntegerField(source='salon.idTblSalon', read_only=True)
    user = serializers.IntegerField(source='user.idTblUser', read_only=True)

    class Meta:
        model = TblFavorite
        fields = ['idTblFavorite', 'user', 'salon', 'added_at']




# # hairbnb/serializers/favorites_serializers.py
#
# from rest_framework import serializers
# from hairbnb.models import TblFavorite
# from hairbnb.salon.salon_serializers import TblSalonSerializer
#
#
# # Ce serializer transforme les objets TblFavorite en une représentation JSON,
# # en incluant les informations du salon associé de manière en lecture seule.
# class TblFavoriteSerializer(serializers.ModelSerializer):
#     salon = TblSalonSerializer(read_only=True)
#
#     class Meta:
#         model = TblFavorite
#         fields = ['idTblFavorite', 'salon']
