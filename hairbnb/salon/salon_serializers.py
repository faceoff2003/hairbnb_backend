from rest_framework import serializers
from hairbnb.models import TblSalon, TblSalonService, TblSalonImage, TblAvis, TblService
from hairbnb.serializers.salon_services_serializers import ServiceSerializer


class SalonSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    proprietaire = serializers.SerializerMethodField()
    adresse_formatee = serializers.SerializerMethodField()

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'proprietaire', 'services', 'nom_salon',
            'slogan', 'a_propos', 'logo_salon', 'position',
            'numero_tva', 'adresse_formatee'
        ]

    def get_services(self, obj):
        # Récupérer les services via la table de liaison
        salon_services = TblSalonService.objects.filter(salon=obj)
        services = [ss.service for ss in salon_services]
        return ServiceSerializer(services, many=True).data

    def get_proprietaire(self, obj):
        # Récupérer la coiffeuse propriétaire du salon
        try:
            proprietaire = obj.get_proprietaire()
            if proprietaire:
                return proprietaire.idTblUser.idTblUser
            return None
        except Exception as e:
            print(f"❌ Erreur get_proprietaire: {e}")  # Debug
            return None

    def get_adresse_formatee(self, obj):
        """Sérialise l'adresse de manière sécurisée"""
        try:
            if obj.adresse:
                return {
                    'numero': obj.adresse.numero,
                    'rue': obj.adresse.rue.nom_rue if obj.adresse.rue else None,
                    'commune': obj.adresse.rue.localite.commune if obj.adresse.rue and obj.adresse.rue.localite else None,
                    'code_postal': obj.adresse.rue.localite.code_postal if obj.adresse.rue and obj.adresse.rue.localite else None
                }
            return None
        except Exception as e:
            print(f"❌ Erreur adresse: {e}")  # Debug
            return None

    def to_representation(self, instance):
        # Conversion standard en dictionnaire
        data = super().to_representation(instance)
        # Pour la compatibilité avec l'ancien code, renommer proprietaire en coiffeuse
        data['coiffeuse'] = data.pop('proprietaire')
        # Renommer adresse_formatee en adresse pour compatibilité
        data['adresse'] = data.pop('adresse_formatee')
        return data


class TblSalonSerializer(serializers.ModelSerializer):
    proprietaire = serializers.SerializerMethodField()
    adresse_formatee = serializers.SerializerMethodField()  # ✅ Ajouté

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'proprietaire', 'nom_salon',
            'slogan', 'logo_salon', 'position',
            'numero_tva', 'adresse_formatee'
        ]

    def get_proprietaire(self, obj):
        # Récupérer la coiffeuse propriétaire du salon
        try:
            proprietaire = obj.get_proprietaire()
            if proprietaire:
                return proprietaire.idTblUser.idTblUser
            return None
        except Exception as e:
            print(f"❌ Erreur get_proprietaire: {e}")  # Debug
            return None

    def get_adresse_formatee(self, obj):
        """Sérialise l'adresse de manière sécurisée"""
        try:
            if obj.adresse:
                return {
                    'numero': obj.adresse.numero,
                    'rue': obj.adresse.rue.nom_rue if obj.adresse.rue else None,
                    'commune': obj.adresse.rue.localite.commune if obj.adresse.rue and obj.adresse.rue.localite else None,
                    'code_postal': obj.adresse.rue.localite.code_postal if obj.adresse.rue and obj.adresse.rue.localite else None
                }
            return None
        except Exception as e:
            print(f"❌ Erreur adresse: {e}")  # Debug
            return None

    def to_representation(self, instance):
        # Conversion standard en dictionnaire
        data = super().to_representation(instance)
        # Pour la compatibilité avec l'ancien code, renommer proprietaire en coiffeuse
        data['coiffeuse'] = data.pop('proprietaire')
        # Renommer adresse_formatee en adresse pour compatibilité
        data['adresse'] = data.pop('adresse_formatee')
        return data


class TblSalonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblSalonImage
        fields = ['id', 'salon', 'image']


class TblAvisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblAvis
        fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
        read_only_fields = ['date']


from rest_framework import serializers
from hairbnb.models import TblSalon, TblCoiffeuse, TblAdresse, TblCoiffeuseSalon


class SalonCreateSerializer(serializers.ModelSerializer):
    """
    Serializer spécialement conçu pour la création de salons.
    Gère automatiquement la relation propriétaire via TblCoiffeuseSalon.
    """

    # Champ obligatoire pour identifier la coiffeuse propriétaire
    coiffeuse_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TblSalon
        fields = [
            'nom_salon',
            'slogan',
            'a_propos',
            'logo_salon',
            'numero_tva',
            'adresse',
            'position',
            'coiffeuse_id'  # Champ pour identifier le propriétaire
        ]
        extra_kwargs = {
            'nom_salon': {'required': True},
            'slogan': {'required': False},
            'a_propos': {'required': False},
            'logo_salon': {'required': False},
            'numero_tva': {'required': False},
            'adresse': {'required': False},
            'position': {'required': False}
        }

    def validate_coiffeuse_id(self, value):
        """Valide que la coiffeuse existe"""
        try:
            coiffeuse = TblCoiffeuse.objects.get(idTblUser=value)
            return value
        except TblCoiffeuse.DoesNotExist:
            raise serializers.ValidationError("La coiffeuse spécifiée n'existe pas.")

    def validate_numero_tva(self, value):
        """Valide l'unicité du numéro de TVA si fourni"""
        if value and TblSalon.objects.filter(numero_tva=value).exists():
            raise serializers.ValidationError("Ce numéro de TVA est déjà utilisé.")
        return value

    def validate_adresse(self, value):
        """Valide que l'adresse existe si fournie"""
        if value:
            try:
                TblAdresse.objects.get(idTblAdresse=value.idTblAdresse)
            except TblAdresse.DoesNotExist:
                raise serializers.ValidationError("L'adresse spécifiée n'existe pas.")
        return value

    def create(self, validated_data):
        """
        Crée le salon et établit automatiquement la relation propriétaire.
        """
        # Extraire l'ID de la coiffeuse des données validées
        coiffeuse_id = validated_data.pop('coiffeuse_id')

        # Récupérer l'objet coiffeuse
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=coiffeuse_id)

        # Créer le salon
        salon = TblSalon.objects.create(**validated_data)

        # Créer la relation propriétaire dans TblCoiffeuseSalon
        TblCoiffeuseSalon.objects.create(
            coiffeuse=coiffeuse,
            salon=salon,
            est_proprietaire=True
        )

        return salon

    def to_representation(self, instance):
        """
        Retourne une représentation complète du salon créé.
        Utilise le SalonSerializer existant pour la réponse.
        """
        return SalonSerializer(instance, context=self.context).data


class ServiceDropdownSerializer(serializers.ModelSerializer):
    """
    Serializer optimisé pour les dropdowns Flutter.
    ID service, nom service, ID catégorie, nom catégorie.
    """
    categorie_id = serializers.SerializerMethodField()
    categorie_nom = serializers.SerializerMethodField()

    class Meta:
        model = TblService
        fields = [
            'idTblService',
            'intitule_service',
            'categorie_id',
            'categorie_nom'
        ]

    def get_categorie_id(self, obj):
        return obj.categorie.idTblCategorie if obj.categorie else None

    def get_categorie_nom(self, obj):
        return obj.categorie.intitule_categorie if obj.categorie else "Sans catégorie"


# class SalonDetailSerializer(serializers.ModelSerializer):
#     idTblSalon = serializers.IntegerField(source='idTblSalon', read_only=True)
#     nom = serializers.CharField(source='nom_salon', read_only=True)
#     slogan = serializers.CharField(read_only=True)
#     logo = serializers.SerializerMethodField()
#     position = serializers.CharField(read_only=True)
#     latitude = serializers.SerializerMethodField()
#     longitude = serializers.SerializerMethodField()
#     coiffeuse_ids = serializers.SerializerMethodField()
#     coiffeuses_details = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'nom', 'slogan', 'logo', 'position',
#             'latitude', 'longitude', 'coiffeuse_ids', 'coiffeuses_details'
#         ]
#
#     def get_logo(self, obj):
#         if obj.logo_salon:
#             return obj.logo_salon.url
#         return None
#
#     def get_latitude(self, obj):
#         if obj.position and ',' in obj.position:
#             return float(obj.position.split(',')[0])
#         return None
#
#     def get_longitude(self, obj):
#         if obj.position and ',' in obj.position:
#             return float(obj.position.split(',')[1])
#         return None
#
#     def get_coiffeuse_ids(self, obj):
#         relations = TblCoiffeuseSalon.objects.filter(salon=obj)
#         return [relation.coiffeuse.idTblUser.idTblUser for relation in relations]
#
#     def get_coiffeuses_details(self, obj):
#         relations = TblCoiffeuseSalon.objects.filter(salon=obj)
#         details = []
#         for relation in relations:
#             coiffeuse = relation.coiffeuse
#             user = coiffeuse.idTblUser
#             details.append({
#                 "idTblCoiffeuse": user.idTblUser,
#                 "idTblUser": user.idTblUser,
#                 "uuid": user.uuid,
#                 "nom": user.nom,
#                 "prenom": user.prenom,
#                 "role": user.get_role(),
#                 "type": user.get_type(),
#                 "est_proprietaire": relation.est_proprietaire,
#                 "nom_commercial": coiffeuse.nom_commercial
#             })
#         return details