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
            'idTblUser', 'denomination_sociale', 'tva', 'position', 'user'
        ]


# 🔹 Serializer COMPLET pour le Client
class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='idTblUser')

    class Meta:
        model = TblClient
        fields = ['idTblUser', 'user']



# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblUser
#         fields = [
#             'idTblUser',
#             'uuid',
#             'nom',
#             'prenom',
#             'email',
#             'type',
#             'sexe',
#             'numero_telephone',
#             'date_naissance',
#             'is_active',
#             'adresse',  # Tu peux ajouter un serializer pour adresse si nécessaire
#             'photo_profil'
#         ]
#
# class CoiffeuseSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser', read_only=True)
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = [
#             'id',
#             'user',  # Inclut toutes les informations de TblUser
#             'denomination_sociale',
#             'tva',
#             'position'
#         ]
#
# class RueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblRue
#         fields = '__all__'  # Inclure tous les champs de la rue
#
# class LocaliteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblLocalite
#         fields = '__all__'  # Inclure tous les champs de la localité
#
# class AdresseSerializer(serializers.ModelSerializer):
#     localite = LocaliteSerializer()  # Inclure la localité
#     rue = RueSerializer()  # Inclure la rue
#
#     class Meta:
#         model = TblAdresse
#         fields = '__all__'
#
# class ClientSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser', read_only=True)
#
#     class Meta:
#         model = TblClient
#         fields = [
#             'id',
#             'user'  # Inclut toutes les informations de TblUser
#         ]
