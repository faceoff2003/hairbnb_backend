from rest_framework import serializers

from hairbnb.models import TblUser, TblCoiffeuse, TblClient
from hairbnb.serializers.users_serializers import CoiffeuseSerializer, ClientSerializer


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer pour récupérer l'utilisateur actuellement connecté,
    qu'il soit Client ou Coiffeuse.
    """
    extra_data = serializers.SerializerMethodField()

    class Meta:
        model = TblUser
        fields = [
            'idTblUser','uuid', 'nom', 'prenom', 'email', 'numero_telephone', 'date_naissance',
            'sexe', 'is_active', 'photo_profil', 'type', 'extra_data'
        ]

    def get_extra_data(self, obj):
        """Retourne les informations spécifiques selon le type d'utilisateur (coiffeuse ou client)."""
        if obj.type == "coiffeuse":
            try:
                coiffeuse = TblCoiffeuse.objects.get(idTblUser=obj)
                return CoiffeuseSerializer(coiffeuse).data
            except TblCoiffeuse.DoesNotExist:
                return None
        elif obj.type == "client":
            try:
                client = TblClient.objects.get(idTblUser=obj)
                return ClientSerializer(client).data
            except TblClient.DoesNotExist:
                return None
        return None