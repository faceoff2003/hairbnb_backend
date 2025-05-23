from django.db import transaction
from rest_framework import serializers
from hairbnb.models import (
    TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse,
    TblRole, TblSexe, TblType, TblSalon, TblCoiffeuseSalon
)
from datetime import datetime




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
        fields = ['idTblAdresse', 'numero', 'rue']


# 🔹 Serializer pour le Rôle
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblRole
        fields = ['idTblRole', 'nom']


# 🔹 Serializer pour le Sexe
class SexeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblSexe
        fields = ['idTblSexe', 'libelle']


# 🔹 Serializer pour le Type
class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblType
        fields = ['idTblType', 'libelle']


# 🔹 Serializer pour l'Utilisateur (User)
class UserSerializer(serializers.ModelSerializer):
    adresse = AdresseSerializer()
    role = RoleSerializer()
    sexe_ref = SexeSerializer()
    type_ref = TypeSerializer()

    class Meta:
        model = TblUser
        fields = [
            'idTblUser', 'uuid', 'nom', 'prenom', 'email', 'numero_telephone',
            'date_naissance', 'is_active', 'photo_profil', 'adresse',
            'role', 'sexe_ref', 'type_ref'
        ]


# 🔹 Serializer simple pour la Coiffeuse (sans user details)
class CoiffeuseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblCoiffeuse
        fields = ['idTblUser', 'nom_commercial']


# 🔹 Serializer COMPLET pour la Coiffeuse
class CoiffeuseSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='idTblUser')

    class Meta:
        model = TblCoiffeuse
        fields = [
            'idTblUser', 'nom_commercial', 'user'
        ]


# 🔹 Serializer COMPLET pour le Client
class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='idTblUser')

    class Meta:
        model = TblClient
        fields = ['idTblUser', 'user']


# 🔹 Serializer simple pour le Salon
class SalonSimpleSerializer(serializers.ModelSerializer):
    adresse = AdresseSerializer(read_only=True)

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'nom_salon', 'slogan', 'logo_salon',
            'adresse', 'position', 'numero_tva'
        ]


# 🔹 Serializer COMPLET pour le Salon
class SalonSerializer(serializers.ModelSerializer):
    adresse = AdresseSerializer(read_only=True)
    coiffeuses = CoiffeuseSimpleSerializer(many=True, read_only=True)
    proprietaire = serializers.SerializerMethodField()

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'nom_salon', 'slogan', 'a_propos',
            'logo_salon', 'adresse', 'position', 'numero_tva',
            'coiffeuses', 'proprietaire'
        ]

    def get_proprietaire(self, obj):
        """Récupère la coiffeuse propriétaire du salon"""
        proprietaire = obj.get_proprietaire()
        if proprietaire:
            return CoiffeuseSimpleSerializer(proprietaire).data
        return None


# 🔹 Serializer pour la relation Coiffeuse-Salon
class CoiffeuseSalonSerializer(serializers.ModelSerializer):
    coiffeuse = CoiffeuseSimpleSerializer(read_only=True)
    salon = SalonSimpleSerializer(read_only=True)

    class Meta:
        model = TblCoiffeuseSalon
        fields = ['idCoiffeuseSalon', 'coiffeuse', 'salon', 'est_proprietaire']


# 🔹 Serializer pour la création complète d'un profil utilisateur (Client ou Coiffeuse)
class UserCreationSerializer(serializers.Serializer):
    """
    Serialiser pour la création complète d'un profil utilisateur.
    Gère la création de l'utilisateur et des objets liés (adresse, type spécifique),
    sans inclure la création de salon ou la relation TblCoiffeuseSalon à ce stade.
    Le rôle par défaut est 'user'.
    """

    # Champs obligatoires de base de l'utilisateur (pour TblUser)
    userUuid = serializers.CharField(max_length=40)
    email = serializers.EmailField()
    # Le 'type' ici correspond à 'Client' ou 'Coiffeuse' dans TblType
    type = serializers.CharField(max_length=15)
    nom = serializers.CharField(max_length=50)
    prenom = serializers.CharField(max_length=50)
    sexe = serializers.CharField(max_length=10)  # 'homme' ou 'femme' (en minuscules)
    telephone = serializers.CharField(max_length=20)
    date_naissance = serializers.CharField()  # Attendu au format DD-MM-YYYY

    # Champs d'adresse (pour TblAdresse, TblRue, TblLocalite)
    code_postal = serializers.CharField(max_length=6)
    commune = serializers.CharField(max_length=40)
    rue = serializers.CharField(max_length=100)
    numero = serializers.CharField(max_length=5)
    boite_postale = serializers.CharField(max_length=10, required=False, allow_blank=True)

    # Champ optionnel pour la coiffeuse (pour TblCoiffeuse)
    nom_commercial = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Photo de profil (fichier)
    photo_profil = serializers.ImageField(required=False, allow_null=True)

    def validate_userUuid(self, value):
        """Vérifie que l'UUID n'existe pas déjà."""
        if TblUser.objects.filter(uuid=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet UUID existe déjà.")
        return value

    def validate_email(self, value):
        """Vérifie que l'email n'existe pas déjà."""
        if TblUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_type(self, value):
        """Vérifie que le type (Client/Coiffeuse) existe dans la table TblType."""
        # CHANGEMENT : Suppression de value_lower = value.lower()
        if value not in ['Client', 'Coiffeuse']: # CHANGEMENT : Les valeurs attendues sont avec majuscule
            raise serializers.ValidationError("Le type doit être 'Client' ou 'Coiffeuse'.")
        try:
            TblType.objects.get(libelle=value) # CHANGEMENT : Recherche avec la valeur exacte reçue
        except TblType.DoesNotExist:
            raise serializers.ValidationError(f"Le type '{value}' n'existe pas dans la table de référence TblType.")
        return value # Retourne la valeur telle quelle

    def validate_sexe(self, value):
        """Vérifie que le sexe existe dans la table de référence."""
        # CHANGEMENT : Suppression de value_lower = value.lower()
        if value not in ['Homme', 'Femme']: # CHANGEMENT : Les valeurs attendues sont avec majuscule
             raise serializers.ValidationError("Le sexe doit être 'Homme' ou 'Femme'.")
        try:
            TblSexe.objects.get(libelle=value) # CHANGEMENT : Recherche avec la valeur exacte reçue
        except TblSexe.DoesNotExist:
            raise serializers.ValidationError(f"Le sexe '{value}' n'existe pas dans la table de référence TblSexe.")
        return value # Retourne la valeur telle quelle

    def validate_date_naissance(self, value):
        """Valide et convertit la date de naissance du format DD-MM-YYYY en objet Date."""
        try:
            date_obj = datetime.strptime(value, '%d-%m-%Y').date()
            return date_obj
        except ValueError:
            raise serializers.ValidationError("Le format de la date de naissance doit être DD-MM-YYYY.")

    def validate(self, attrs):
        """Validation croisée pour les champs dépendant du type d'utilisateur."""
        # Pour une coiffeuse, le nom_commercial est obligatoire
        if attrs['type'] == 'coiffeuse' and not attrs.get('nom_commercial'):
            raise serializers.ValidationError({
                'nom_commercial': 'Le nom commercial est obligatoire pour un type coiffeuse.'
            })
        return attrs

    def create(self, validated_data):
        """Crée un utilisateur complet, son adresse, son rôle par défaut et son profil spécifique (Coiffeuse/Client)."""
        with transaction.atomic():
            # Récupérer les objets de référence basés sur les valeurs validées
            # Le rôle par défaut pour les utilisateurs créés via cette API est 'user'
            role_obj = TblRole.objects.get(nom='user') # Le rôle par défaut est 'user'
            sexe_obj = TblSexe.objects.get(libelle=validated_data['sexe'])
            type_obj = TblType.objects.get(libelle=validated_data['type'])

            # Créer ou récupérer la localité
            localite, _ = TblLocalite.objects.get_or_create(
                commune=validated_data['commune'],
                code_postal=validated_data['code_postal']
            )

            # Créer ou récupérer la rue
            rue, _ = TblRue.objects.get_or_create(
                nom_rue=validated_data['rue'],
                localite=localite
            )

            # Gérer le format du numéro de rue (avec ou sans boîte postale)
            numero_rue_complet = validated_data['numero']
            if validated_data.get('boite_postale'):
                numero_rue_complet = f"{numero_rue_complet}/{validated_data['boite_postale']}"

            # Créer l'adresse
            adresse = TblAdresse.objects.create(
                numero=numero_rue_complet,
                rue=rue
            )

            # Créer l'utilisateur principal
            user = TblUser.objects.create(
                uuid=validated_data['userUuid'],
                nom=validated_data['nom'],
                prenom=validated_data['prenom'],
                email=validated_data['email'],
                numero_telephone=validated_data['telephone'],
                date_naissance=validated_data['date_naissance'],
                adresse=adresse,
                role=role_obj,      # Assigne le rôle 'user'
                sexe_ref=sexe_obj,  # Assigne la référence du sexe
                type_ref=type_obj,  # Assigne la référence du type (Client/Coiffeuse)
                photo_profil=validated_data.get('photo_profil')
            )

            # Créer l'objet spécifique au type (Coiffeuse ou Client)
            if validated_data['type'] == 'Coiffeuse':
                TblCoiffeuse.objects.create(
                    idTblUser=user,
                    nom_commercial=validated_data.get('nom_commercial')
                )
            elif validated_data['type'] == 'Client':
                TblClient.objects.create(idTblUser=user)

            return user

    def to_representation(self, instance):
        """Personnalise la réponse de sortie après la création de l'utilisateur."""
        return {
            'user_id': instance.idTblUser,
            'uuid': instance.uuid,
            'nom': instance.nom,
            'prenom': instance.prenom,
            'email': instance.email,
            'type': instance.get_type(), # Appelle la méthode get_type() de TblUser
            'role': instance.get_role(), # Appelle la méthode get_role() de TblUser
            'created': True
        }



# # 🔹 Serializer pour la création complète d'un profil utilisateur
# class UserCreationSerializer(serializers.Serializer):
#     """
#     Serializer pour la création complète d'un profil utilisateur.
#     Gère la création de l'utilisateur et des objets liés (adresse, rôle spécifique).
#     """
#
#     # Champs obligatoires de base
#     userUuid = serializers.CharField(max_length=40)
#     email = serializers.EmailField()
#     role = serializers.CharField(max_length=15)  # "client" ou "coiffeuse"
#     nom = serializers.CharField(max_length=50)
#     prenom = serializers.CharField(max_length=50)
#     sexe = serializers.CharField(max_length=10)
#     telephone = serializers.CharField(max_length=20)
#     date_naissance = serializers.CharField()  # Format DD-MM-YYYY
#
#     # Champs d'adresse
#     code_postal = serializers.CharField(max_length=6)
#     commune = serializers.CharField(max_length=40)
#     rue = serializers.CharField(max_length=100)
#     numero = serializers.CharField(max_length=5)
#     boite_postale = serializers.CharField(max_length=10, required=False, allow_blank=True)
#
#     # Champs optionnels pour coiffeuse
#     nom_commercial = serializers.CharField(max_length=50, required=False, allow_blank=True)
#
#     # Photo de profil (optionnelle)
#     photo_profil = serializers.ImageField(required=False, allow_null=True)
#
#     def validate_userUuid(self, value):
#         """Vérifier que l'UUID n'existe pas déjà"""
#         if TblUser.objects.filter(uuid=value).exists():
#             raise serializers.ValidationError("Un utilisateur avec cet UUID existe déjà")
#         return value
#
#     def validate_email(self, value):
#         """Vérifier que l'email n'existe pas déjà"""
#         if TblUser.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Un utilisateur avec cet email existe déjà")
#         return value
#
#     def validate_role(self, value):
#         """Vérifier que le rôle existe"""
#         try:
#             TblRole.objects.get(nom=value)
#             TblType.objects.get(libelle=value)
#         except (TblRole.DoesNotExist, TblType.DoesNotExist):
#             raise serializers.ValidationError(f"Le rôle '{value}' n'existe pas")
#         return value
#
#     def validate_sexe(self, value):
#         """Vérifier que le sexe existe"""
#         try:
#             TblSexe.objects.get(libelle=value)
#         except TblSexe.DoesNotExist:
#             raise serializers.ValidationError(f"Le sexe '{value}' n'existe pas")
#         return value
#
#     def validate_date_naissance(self, value):
#         """Valider et convertir la date de naissance"""
#         try:
#             date_obj = datetime.strptime(value, '%d-%m-%Y').date()
#             return date_obj
#         except ValueError:
#             raise serializers.ValidationError("Le format de la date doit être DD-MM-YYYY")
#
#     def validate(self, attrs):
#         """Validation croisée"""
#         # Si c'est une coiffeuse, le nom commercial est obligatoire
#         if attrs['role'].lower() == 'coiffeuse' and not attrs.get('nom_commercial'):
#             raise serializers.ValidationError({
#                 'nom_commercial': 'Le nom commercial est obligatoire pour une coiffeuse'
#             })
#         return attrs
#
#     def create(self, validated_data):
#         """Création complète de l'utilisateur et objets liés"""
#
#         # Récupérer les objets de référence
#         role_obj = TblRole.objects.get(nom=validated_data['role'])
#         sexe_obj = TblSexe.objects.get(libelle=validated_data['sexe'])
#         type_obj = TblType.objects.get(libelle=validated_data['role'])
#
#         # Créer ou récupérer l'adresse
#         localite, _ = TblLocalite.objects.get_or_create(
#             commune=validated_data['commune'],
#             code_postal=validated_data['code_postal']
#         )
#
#         rue, _ = TblRue.objects.get_or_create(
#             nom_rue=validated_data['rue'],
#             localite=localite
#         )
#
#         # Gérer le numéro avec boîte postale optionnelle
#         numero = validated_data['numero']
#         if validated_data.get('boite_postale'):
#             numero = f"{numero}/{validated_data['boite_postale']}"
#
#         adresse = TblAdresse.objects.create(
#             numero=numero,
#             rue=rue
#         )
#
#         # Calculer les coordonnées géographiques (optionnel)
#         try:
#             adresse_complete = f"{validated_data['numero']}, {validated_data['rue']}, {validated_data['commune']}, {validated_data['code_postal']}"
#             latitude, longitude = GeolocationService.geocode_address(adresse_complete)
#         except Exception as e:
#             print(f"Erreur géolocalisation: {e}")
#             latitude, longitude = None, None
#
#         # Créer l'utilisateur principal
#         user = TblUser.objects.create(
#             uuid=validated_data['userUuid'],
#             nom=validated_data['nom'],
#             prenom=validated_data['prenom'],
#             email=validated_data['email'],
#             numero_telephone=validated_data['telephone'],
#             date_naissance=validated_data['date_naissance'],
#             adresse=adresse,
#             role=role_obj,
#             sexe_ref=sexe_obj,
#             type_ref=type_obj,
#             photo_profil=validated_data.get('photo_profil')
#         )
#
#         # Créer l'objet spécifique selon le rôle
#         if validated_data['role'].lower() == 'coiffeuse':
#             coiffeuse = TblCoiffeuse.objects.create(
#                 idTblUser=user,
#                 nom_commercial=validated_data.get('nom_commercial')
#             )
#             # Stocker les coordonnées si nécessaire (vous pouvez les ajouter au modèle)
#             user.coiffeuse_info = coiffeuse
#
#         elif validated_data['role'].lower() == 'client':
#             client = TblClient.objects.create(idTblUser=user)
#             user.client_info = client
#
#         return user
#
#     def to_representation(self, instance):
#         """Personnaliser la réponse de sortie"""
#         return {
#             'user_id': instance.idTblUser,
#             'uuid': instance.uuid,
#             'nom': instance.nom,
#             'prenom': instance.prenom,
#             'email': instance.email,
#             'type': instance.get_type(),
#             'role': instance.get_role(),
#             'created': True
#         }






# from rest_framework import serializers
# from hairbnb.models import (
#     TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse,
#     TblRole, TblSexe, TblType,TblSalon, TblCoiffeuseSalon
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
#         fields = ['idTblAdresse', 'numero', 'rue']
#
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#
#         # Si le numéro contient "/", on extrait la partie après comme boîte postale
#         if representation['numero'] and '/' in representation['numero']:
#             parts = representation['numero'].split('/')
#             representation['numero'] = parts[0]
#             representation['boite_postale'] = parts[1]
#         else:
#             representation['boite_postale'] = None
#
#         return representation
#
#
# # 🔹 Serializer pour le Numéro TVA
# class NumeroTVASerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblNumeroTVA
#         fields = ['idTblNumeroTVA', 'numero_tva']
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
# # 🔹 Serializer simple pour la Coiffeuse (sans user details)
# class CoiffeuseSimpleSerializer(serializers.ModelSerializer):
#     numero_tva = NumeroTVASerializer()
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = ['idTblUser', 'nom_commercial', 'numero_tva']
#
#
# # 🔹 Serializer COMPLET pour la Coiffeuse
# class CoiffeuseSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source='idTblUser')
#     numero_tva = NumeroTVASerializer()
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = [
#             'idTblUser', 'nom_commercial', 'numero_tva', 'user'
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
#
#
# # 🔹 Serializer simple pour le Salon
# class SalonSimpleSerializer(serializers.ModelSerializer):
#     numero_tva = NumeroTVASerializer(read_only=True)
#     adresse = AdresseSerializer(read_only=True)
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'nom_salon', 'slogan', 'logo_salon',
#             'adresse', 'position', 'numero_tva'
#         ]
#
#
# # 🔹 Serializer COMPLET pour le Salon
# class SalonSerializer(serializers.ModelSerializer):
#     coiffeuse = CoiffeuseSimpleSerializer(read_only=True)
#     numero_tva = NumeroTVASerializer(read_only=True)
#     adresse = AdresseSerializer(read_only=True)
#     coiffeuses = CoiffeuseSimpleSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'a_propos',
#             'logo_salon', 'adresse', 'position', 'numero_tva', 'coiffeuses'
#         ]
#
#
# # 🔹 Serializer pour la relation Coiffeuse-Salon
# class CoiffeuseSalonSerializer(serializers.ModelSerializer):
#     coiffeuse = CoiffeuseSimpleSerializer(read_only=True)
#     salon = SalonSimpleSerializer(read_only=True)
#
#     class Meta:
#         model = TblCoiffeuseSalon
#         fields = ['idCoiffeuseSalon', 'coiffeuse', 'salon', 'est_proprietaire']
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # from rest_framework import serializers
# # from hairbnb.models import (
# #     TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse,
# #     TblRole, TblSexe, TblType, TblNumeroTVA, TblSalon, TblCoiffeuseSalon
# # )
# #
# #
# # # 🔹 Serializer pour la Localité
# # class LocaliteSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblLocalite
# #         fields = ['idTblLocalite', 'commune', 'code_postal']
# #
# #
# # # 🔹 Serializer pour la Rue
# # class RueSerializer(serializers.ModelSerializer):
# #     localite = LocaliteSerializer()
# #
# #     class Meta:
# #         model = TblRue
# #         fields = ['idTblRue', 'nom_rue', 'localite']
# #
# #
# # # 🔹 Serializer pour la Boîte Postale
# # class BoitePostaleSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblBoitePostale
# #         fields = ['idTblBoitePostale', 'numero_bp']
# #
# #
# # # 🔹 Serializer pour l'Adresse
# # class AdresseSerializer(serializers.ModelSerializer):
# #     rue = RueSerializer()
# #     boites_postales = BoitePostaleSerializer(many=True, read_only=True)
# #
# #     class Meta:
# #         model = TblAdresse
# #         fields = ['idTblAdresse', 'numero', 'rue', 'boites_postales']
# #
# #
# # # 🔹 Serializer pour le Numéro TVA
# # class NumeroTVASerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblNumeroTVA
# #         fields = ['idTblNumeroTVA', 'numero_tva']
# #
# #
# # # 🔹 Serializer pour le Rôle
# # class RoleSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblRole
# #         fields = ['idTblRole', 'nom']
# #
# #
# # # 🔹 Serializer pour le Sexe
# # class SexeSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblSexe
# #         fields = ['idTblSexe', 'libelle']
# #
# #
# # # 🔹 Serializer pour le Type
# # class TypeSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblType
# #         fields = ['idTblType', 'libelle']
# #
# #
# # # 🔹 Serializer pour l'Utilisateur (User)
# # class UserSerializer(serializers.ModelSerializer):
# #     adresse = AdresseSerializer()
# #     role = RoleSerializer()
# #     sexe_ref = SexeSerializer()
# #     type_ref = TypeSerializer()
# #
# #     class Meta:
# #         model = TblUser
# #         fields = [
# #             'idTblUser', 'uuid', 'nom', 'prenom', 'email', 'numero_telephone',
# #             'date_naissance', 'is_active', 'photo_profil', 'adresse',
# #             'role', 'sexe_ref', 'type_ref'
# #         ]
# #
# #
# # # 🔹 Serializer simple pour la Coiffeuse (sans user details)
# # class CoiffeuseSimpleSerializer(serializers.ModelSerializer):
# #     numero_tva = NumeroTVASerializer()
# #
# #     class Meta:
# #         model = TblCoiffeuse
# #         fields = ['idTblUser', 'nom_commercial', 'numero_tva']
# #
# #
# # # 🔹 Serializer COMPLET pour la Coiffeuse
# # class CoiffeuseSerializer(serializers.ModelSerializer):
# #     user = UserSerializer(source='idTblUser')
# #     numero_tva = NumeroTVASerializer()
# #
# #     class Meta:
# #         model = TblCoiffeuse
# #         fields = [
# #             'idTblUser', 'nom_commercial', 'numero_tva', 'user'
# #         ]
# #
# #
# # # 🔹 Serializer COMPLET pour le Client
# # class ClientSerializer(serializers.ModelSerializer):
# #     user = UserSerializer(source='idTblUser')
# #
# #     class Meta:
# #         model = TblClient
# #         fields = ['idTblUser', 'user']
# #
# #
# # # 🔹 Serializer simple pour le Salon
# # class SalonSimpleSerializer(serializers.ModelSerializer):
# #     numero_tva = NumeroTVASerializer(read_only=True)
# #     adresse = AdresseSerializer(read_only=True)
# #
# #     class Meta:
# #         model = TblSalon
# #         fields = [
# #             'idTblSalon', 'nom_salon', 'slogan', 'logo_salon',
# #             'adresse', 'position', 'numero_tva'
# #         ]
# #
# #
# # # 🔹 Serializer COMPLET pour le Salon
# # class SalonSerializer(serializers.ModelSerializer):
# #     coiffeuse = CoiffeuseSimpleSerializer(read_only=True)
# #     numero_tva = NumeroTVASerializer(read_only=True)
# #     adresse = AdresseSerializer(read_only=True)
# #     coiffeuses = CoiffeuseSimpleSerializer(many=True, read_only=True)
# #
# #     class Meta:
# #         model = TblSalon
# #         fields = [
# #             'idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'a_propos',
# #             'logo_salon', 'adresse', 'position', 'numero_tva', 'coiffeuses'
# #         ]
# #
# #
# # # 🔹 Serializer pour la relation Coiffeuse-Salon
# # class CoiffeuseSalonSerializer(serializers.ModelSerializer):
# #     coiffeuse = CoiffeuseSimpleSerializer(read_only=True)
# #     salon = SalonSimpleSerializer(read_only=True)
# #
# #     class Meta:
# #         model = TblCoiffeuseSalon
# #         fields = ['idCoiffeuseSalon', 'coiffeuse', 'salon', 'est_proprietaire']
#
#
#
# # from rest_framework import serializers
# # from hairbnb.models import (
# #     TblUser, TblCoiffeuse, TblClient, TblRue, TblLocalite, TblAdresse,
# #     TblRole, TblSexe, TblType
# # )
# #
# #
# # # 🔹 Serializer pour la Localité
# # class LocaliteSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblLocalite
# #         fields = ['idTblLocalite', 'commune', 'code_postal']
# #
# #
# # # 🔹 Serializer pour la Rue
# # class RueSerializer(serializers.ModelSerializer):
# #     localite = LocaliteSerializer()
# #
# #     class Meta:
# #         model = TblRue
# #         fields = ['idTblRue', 'nom_rue', 'localite']
# #
# #
# # # 🔹 Serializer pour l'Adresse
# # class AdresseSerializer(serializers.ModelSerializer):
# #     rue = RueSerializer()
# #
# #     class Meta:
# #         model = TblAdresse
# #         fields = ['idTblAdresse', 'numero', 'boite_postale', 'rue']
# #
# #
# # # 🔹 Serializer pour le Rôle
# # class RoleSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblRole
# #         fields = ['idTblRole', 'nom']
# #
# #
# # # 🔹 Serializer pour le Sexe
# # class SexeSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblSexe
# #         fields = ['idTblSexe', 'libelle']
# #
# #
# # # 🔹 Serializer pour le Type
# # class TypeSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TblType
# #         fields = ['idTblType', 'libelle']
# #
# #
# # # 🔹 Serializer pour l'Utilisateur (User)
# # class UserSerializer(serializers.ModelSerializer):
# #     adresse = AdresseSerializer()
# #     role = RoleSerializer()
# #     sexe_ref = SexeSerializer()
# #     type_ref = TypeSerializer()
# #
# #     class Meta:
# #         model = TblUser
# #         fields = [
# #             'idTblUser', 'uuid', 'nom', 'prenom', 'email', 'numero_telephone',
# #             'date_naissance', 'is_active', 'photo_profil', 'adresse',
# #             'role', 'sexe_ref', 'type_ref'
# #         ]
# #
# #
# # # 🔹 Serializer COMPLET pour la Coiffeuse
# # class CoiffeuseSerializer(serializers.ModelSerializer):
# #     user = UserSerializer(source='idTblUser')
# #
# #     class Meta:
# #         model = TblCoiffeuse
# #         fields = [
# #             'idTblUser', 'denomination_sociale', 'tva', 'position', 'user'
# #         ]
# #
# #
# # # 🔹 Serializer COMPLET pour le Client
# # class ClientSerializer(serializers.ModelSerializer):
# #     user = UserSerializer(source='idTblUser')
# #
# #     class Meta:
# #         model = TblClient
# #         fields = ['idTblUser', 'user']