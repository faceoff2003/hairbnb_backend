# hairbnb/serializers/favorites_serializers.py

from rest_framework import serializers
from hairbnb.models import TblFavorite
from hairbnb.serializers.salon_services_serializers import TblSalonSerializer


# Ce serializer transforme les objets TblFavorite en une représentation JSON,
# en incluant les informations du salon associé de manière en lecture seule.
class TblFavoriteSerializer(serializers.ModelSerializer):
    salon = TblSalonSerializer(read_only=True)

    class Meta:
        model = TblFavorite
        fields = ['idTblFavorite', 'salon']
