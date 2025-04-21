from rest_framework import serializers
from hairbnb.models import TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse


# 🔹 Serializer pour la Localité
class LocaliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblLocalite
        fields = ['idTblLocalite', 'commune', 'code_postal']


# 🔹 Serializer pour la Rue
class RueSerializer(serializers.ModelSerializer):
    localite = LocaliteSerializer()

    class Meta:
        model = TblRue
        fields = ['idTblRue', 'nom_rue', 'localite']


# 🔹 Serializer pour l'Adresse
class AdresseSerializer(serializers.ModelSerializer):
    rue = RueSerializer()

    class Meta:
        model = TblAdresse
        fields = ['idTblAdresse', 'numero', 'boite_postale', 'rue']


# 🔹 Serializer pour l'Utilisateur (User)
class UserSerializer(serializers.ModelSerializer):
    adresse = AdresseSerializer()

    class Meta:
        model = TblUser
        fields = [
            'uuid', 'nom', 'prenom', 'email', 'numero_telephone', 'date_naissance',
            'sexe', 'is_active', 'photo_profil', 'type', 'adresse'
        ]


# 🔹 Serializer COMPLET pour la Coiffeuse
class CoiffeuseSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='idTblUser')

    class Meta:
        model = TblCoiffeuse
        fields = [
            'id', 'idTblUser', 'denomination_sociale', 'tva', 'position', 'user'
        ]


# 🔹 Serializer COMPLET pour le Client
class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='idTblUser')

    class Meta:
        model = TblClient
        fields = ['idTblUser', 'user']


# class CurrentUserSerializer(serializers.ModelSerializer):
#     """
#     Serializer pour récupérer l'utilisateur actuellement connecté,
#     qu'il soit Client ou Coiffeuse.
#     """
#     extra_data = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblUser
#         fields = [
#             'idTblUser','uuid', 'nom', 'prenom', 'email', 'numero_telephone', 'date_naissance',
#             'sexe', 'is_active', 'photo_profil', 'type', 'extra_data'
#         ]
#
#     def get_extra_data(self, obj):
#         """Retourne les informations spécifiques selon le type d'utilisateur (coiffeuse ou client)."""
#         if obj.type == "coiffeuse":
#             try:
#                 coiffeuse = TblCoiffeuse.objects.get(idTblUser=obj)
#                 return CoiffeuseSerializer(coiffeuse).data
#             except TblCoiffeuse.DoesNotExist:
#                 return None
#         elif obj.type == "client":
#             try:
#                 client = TblClient.objects.get(idTblUser=obj)
#                 return ClientSerializer(client).data
#             except TblClient.DoesNotExist:
#                 return None
#         return None



