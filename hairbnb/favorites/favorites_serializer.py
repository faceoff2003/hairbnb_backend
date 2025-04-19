# hairbnb/serializers/favorites_serializers.py

from rest_framework import serializers
from hairbnb.models import TblFavorite

class TblFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblFavorite
        fields = ['idTblFavorite', 'user', 'salon', 'added_at']
