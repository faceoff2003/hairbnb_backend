# from rest_framework import serializers
# from hairbnb.models import (
#     TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse,
#     TblRole, TblSexe, TblType
# )
#
#
# # 🔹 Serializer pour la Localité
# class LocaliteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblLocalite
#         fields = ['idTblLocalite', 'commune', 'code_postal']
#
#
# # 🔹 Serializer pour la Rue
# class RueSerializer(serializers.ModelSerializer):
#     localite = LocaliteSerializer()
#
#     class Meta:
#         model = TblRue
#         fields = ['idTblRue', 'nom_rue', 'localite']
#
#
# # 🔹 Serializer pour l'Adresse
# class AdresseSerializer(serializers.ModelSerializer):
#     rue = RueSerializer()
#
#     class Meta:
#         model = TblAdresse
#         fields = ['idTblAdresse', 'numero', 'boite_postale', 'rue']
#
#
# # 🔹 Serializer pour le Rôle
# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblRole
#         fields = ['idTblRole', 'nom']
#
#
# # 🔹 Serializer pour le Sexe
# class SexeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSexe
#         fields = ['idTblSexe', 'libelle']
#
#
# # 🔹 Serializer pour le Type
# class TypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblType
#         fields = ['idTblType', 'libelle']
#
#
# # 🔹 Serializer pour l'Utilisateur (User)
# class UserSerializer(serializers.ModelSerializer):
#     adresse = AdresseSerializer()
#     role = RoleSerializer()
#     sexe_ref = SexeSerializer()
#     type_ref = TypeSerializer()
#
#     class Meta:
#         model = TblUser
#         fields = [
#             'idTblUser', 'uuid', 'nom', 'prenom', 'email', 'numero_telephone',
#             'date_naissance', 'is_active', 'photo_profil', 'adresse',
#             'role', 'sexe_ref', 'type_ref'
#         ]
#
#
# # 🔹 Serializer COMPLET pour la Coiffeuse
# class CoiffeuseSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser')
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = [
#             'idTblUser', 'denomination_sociale', 'tva', 'position', 'user'
#         ]
#
#
# # 🔹 Serializer COMPLET pour le Client
# class ClientSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser')
#
#     class Meta:
#         model = TblClient
#         fields = ['idTblUser', 'user']









# from rest_framework import serializers
# from hairbnb.models import TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse
#
#
# # 🔹 Serializer pour la Localité
# class LocaliteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblLocalite
#         fields = ['idTblLocalite', 'commune', 'code_postal']
#
#
# # 🔹 Serializer pour la Rue
# class RueSerializer(serializers.ModelSerializer):
#     localite = LocaliteSerializer()
#
#     class Meta:
#         model = TblRue
#         fields = ['idTblRue', 'nom_rue', 'localite']
#
#
# # 🔹 Serializer pour l'Adresse
# class AdresseSerializer(serializers.ModelSerializer):
#     rue = RueSerializer()
#
#     class Meta:
#         model = TblAdresse
#         fields = ['idTblAdresse', 'numero', 'boite_postale', 'rue']
#
#
# # 🔹 Serializer pour l'Utilisateur (User)
# class UserSerializer(serializers.ModelSerializer):
#     adresse = AdresseSerializer()
#
#     class Meta:
#         model = TblUser
#         fields = [
#             'uuid', 'nom', 'prenom', 'email', 'numero_telephone', 'date_naissance',
#             'sexe', 'is_active', 'photo_profil', 'type', 'adresse'
#         ]
#
#
# # 🔹 Serializer COMPLET pour la Coiffeuse
# class CoiffeuseSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser')
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = [
#             'id', 'idTblUser', 'denomination_sociale', 'tva', 'position', 'user'
#         ]
#
#
# # 🔹 Serializer COMPLET pour le Client
# class ClientSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser')
#
#     class Meta:
#         model = TblClient
#         fields = ['idTblUser', 'user']