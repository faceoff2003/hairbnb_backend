from rest_framework import serializers
from hairbnb.models import TblSalon, TblSalonService, TblSalonImage, TblAvis, TblCoiffeuseSalon
from hairbnb.serializers.salon_services_serializers import ServiceSerializer


class SalonSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    proprietaire = serializers.SerializerMethodField()
    adresse_formatee = serializers.SerializerMethodField()  # ✅ Ajouté pour éviter les erreurs d'adresse

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'proprietaire', 'services', 'nom_salon',
            'slogan', 'a_propos', 'logo_salon', 'position',
            'numero_tva', 'adresse_formatee'  # ✅ Ajouté numero_tva et adresse_formatee
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
            'numero_tva', 'adresse_formatee'  # ✅ Ajouté numero_tva et adresse_formatee
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




# from rest_framework import serializers
# from hairbnb.models import TblSalon, TblSalonService, TblSalonImage, TblAvis, TblCoiffeuseSalon
# from hairbnb.serializers.salon_services_serializers import ServiceSerializer
#
#
# class SalonSerializer(serializers.ModelSerializer):
#     services = serializers.SerializerMethodField()
#     proprietaire = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'proprietaire', 'services', 'nom_salon',
#             'slogan', 'a_propos', 'logo_salon', 'position', 'adresse'
#         ]
#
#     def get_services(self, obj):
#         # Récupérer les services via la table de liaison
#         salon_services = TblSalonService.objects.filter(salon=obj)
#         services = [ss.service for ss in salon_services]
#         return ServiceSerializer(services, many=True).data
#
#     def get_proprietaire(self, obj):
#         # Récupérer la coiffeuse propriétaire du salon
#         proprietaire = obj.get_proprietaire()
#         if proprietaire:
#             return proprietaire.idTblUser.idTblUser
#         return None
#
#     def to_representation(self, instance):
#         # Conversion standard en dictionnaire
#         data = super().to_representation(instance)
#
#         # Pour la compatibilité avec l'ancien code, renommer proprietaire en coiffeuse
#         data['coiffeuse'] = data.pop('proprietaire')
#
#         return data
#
#
# class TblSalonSerializer(serializers.ModelSerializer):
#     proprietaire = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'proprietaire', 'nom_salon',
#             'slogan', 'logo_salon', 'position', 'adresse'
#         ]
#
#     def get_proprietaire(self, obj):
#         # Récupérer la coiffeuse propriétaire du salon
#         proprietaire = obj.get_proprietaire()
#         if proprietaire:
#             return proprietaire.idTblUser.idTblUser
#         return None
#
#     def to_representation(self, instance):
#         # Conversion standard en dictionnaire
#         data = super().to_representation(instance)
#
#         # Pour la compatibilité avec l'ancien code, renommer proprietaire en coiffeuse
#         data['coiffeuse'] = data.pop('proprietaire')
#
#         return data
#
#
# class TblSalonImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalonImage
#         fields = ['id', 'salon', 'image']
#
#
# class TblAvisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblAvis
#         fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
#         read_only_fields = ['date']
#
#







# from rest_framework import serializers
#
# from hairbnb.models import TblSalon, TblSalonService, TblSalonImage, TblAvis
# from hairbnb.serializers.salon_services_serializers import ServiceSerializer
#
#
# class SalonSerializer(serializers.ModelSerializer):
#     services = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'services', 'nom_salon', 'slogan', 'a_propos', 'logo_salon', 'position',
#                   'adresse']
#
#     def get_services(self, obj):
#         # Récupérer les services via la table de liaison
#         salon_services = TblSalonService.objects.filter(salon=obj)
#         services = [ss.service for ss in salon_services]
#         return ServiceSerializer(services, many=True).data
#
#
# class TblSalonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'logo_salon', 'position', 'adresse']
#
#
# class TblSalonImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalonImage
#         fields = ['id', 'salon', 'image']
#
#
# class TblAvisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblAvis
#         fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
#         read_only_fields = ['date']
