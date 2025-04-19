from rest_framework import serializers
from django.utils.timezone import now
from hairbnb.models import (
    TblUser, TblCoiffeuse, TblService, TblSalonImage,
    TblAvis, TblSalon, TblPromotion
)

# Serializer utilisateur
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblUser
        fields = ['idTblUser','nom', 'prenom', 'photo_profil', 'numero_telephone']


# Serializer coiffeuse
class CoiffeuseSerializer(serializers.ModelSerializer):
    idTblUser = UserSerializer(read_only=True)

    class Meta:
        model = TblCoiffeuse
        fields = ['idTblUser', 'denomination_sociale', 'position']


# Serializer images du salon
class SalonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblSalonImage
        fields = ['id', 'image']


# Serializer avis clients
class AvisSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    date_format = serializers.SerializerMethodField()

    class Meta:
        model = TblAvis
        fields = ['note', 'commentaire', 'client_nom', 'date_format']

    def get_client_nom(self, obj):
        if obj.client:
            return f"{obj.client.idTblUser.prenom} {obj.client.idTblUser.nom}"
        return "Anonyme"

    def get_date_format(self, obj):
        return "about a year ago"  # à adapter selon le contexte


# 🔁 Serializer pour les services avec promotion active
class ServiceWithPromotionSerializer(serializers.ModelSerializer):
    prix = serializers.SerializerMethodField()
    duree = serializers.SerializerMethodField()
    promotion_active = serializers.SerializerMethodField()

    class Meta:
        model = TblService
        fields = [
            'idTblService', 'intitule_service', 'description',
            'prix', 'duree', 'promotion_active'
        ]

    def get_prix(self, obj):
        service_prix = obj.service_prix.first()
        if service_prix:
            return service_prix.prix.prix
        return None

    def get_duree(self, obj):
        service_temps = obj.service_temps.first()
        if service_temps:
            return service_temps.temps.minutes
        return None

    def get_promotion_active(self, service):
        promotion = TblPromotion.objects.filter(
            service=service,
            start_date__lte=now(),
            end_date__gte=now()
        ).first()

        if promotion:
            return {
                "discount_percentage": str(promotion.discount_percentage),
                "start_date": promotion.start_date,
                "end_date": promotion.end_date
            }
        return None


# 🏠 Serializer principal pour le salon
class SalonDetailSerializer(serializers.ModelSerializer):
    coiffeuse = CoiffeuseSerializer(read_only=True)
    images = SalonImageSerializer(many=True, read_only=True)
    avis = AvisSerializer(many=True, read_only=True)
    services = serializers.SerializerMethodField()
    adresse = serializers.SerializerMethodField()
    horaires = serializers.SerializerMethodField()
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon', 'nom_salon', 'slogan', 'a_propos', 'logo_salon',
            'coiffeuse', 'adresse', 'horaires', 'note_moyenne', 'nombre_avis',
            'images', 'avis', 'services'
        ]

    def get_services(self, obj):
        services = TblService.objects.filter(salon_service__salon=obj)
        return ServiceWithPromotionSerializer(services, many=True).data

    def get_adresse(self, obj):
        user = obj.coiffeuse.idTblUser
        if user.adresse:
            return f"{user.adresse.numero} {user.adresse.rue.nom_rue}, {user.adresse.rue.localite.commune}, {user.adresse.rue.localite.code_postal}"
        return None

    def get_horaires(self, obj):
        horaires = obj.coiffeuse.horaires.all().order_by('jour')
        if horaires:
            jours = {
                0: "Mon", 1: "Tue", 2: "Wed",
                3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"
            }
            return ", ".join(
                f"{h.heure_debut.strftime('%I:%M %p')} - {h.heure_fin.strftime('%I:%M %p')} / {jours[h.jour]}"
                for h in horaires
            )
        return "10:00 AM - 6:00 PM / Mon - Fri"

    def get_note_moyenne(self, obj):
        avis = obj.avis.all()
        if avis:
            return round(sum(a.note for a in avis) / len(avis), 1)
        return 0

    def get_nombre_avis(self, obj):
        return obj.avis.count()







# from rest_framework import serializers
#
# from hairbnb.models import TblUser, TblCoiffeuse, TblPrix, TblTemps, TblService, TblSalonImage, TblAvis, TblSalon
#
#
# # Serializer pour l'utilisateur (informations de base)
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblUser
#         fields = ['nom', 'prenom', 'photo_profil', 'numero_telephone']
#
#
# # Serializer pour la coiffeuse
# class CoiffeuseSerializer(serializers.ModelSerializer):
#     idTblUser = UserSerializer(read_only=True)
#
#     class Meta:
#         model = TblCoiffeuse
#         fields = ['idTblUser', 'denomination_sociale', 'position']
#
#
# # Serializer pour les prix des services
# class PrixSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblPrix
#         fields = ['prix']
#
#
# # Serializer pour les temps des services
# class TempsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblTemps
#         fields = ['minutes']
#
#
# # Serializer pour les services avec prix et durée
# class ServiceDetailSerializer(serializers.ModelSerializer):
#     prix = serializers.SerializerMethodField()
#     duree = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblService
#         fields = ['idTblService', 'intitule_service', 'description', 'prix', 'duree']
#
#     def get_prix(self, obj):
#         service_prix = obj.service_prix.first()
#         if service_prix:
#             return service_prix.prix.prix
#         return None
#
#     def get_duree(self, obj):
#         service_temps = obj.service_temps.first()
#         if service_temps:
#             return service_temps.temps.minutes
#         return None
#
#
# # Serializer pour les images du salon
# class SalonImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalonImage
#         fields = ['image']
#
#
# # Serializer pour les avis clients
# class AvisSerializer(serializers.ModelSerializer):
#     client_nom = serializers.SerializerMethodField()
#     date_format = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblAvis
#         fields = ['note', 'commentaire', 'client_nom', 'date_format']
#
#     def get_client_nom(self, obj):
#         if obj.client:
#             return f"{obj.client.idTblUser.prenom} {obj.client.idTblUser.nom}"
#         return "Anonyme"
#
#     def get_date_format(self, obj):
#         # Formater la date comme "about a year ago"
#         return "about a year ago"  # À personnaliser selon vos besoins
#
#
# # Serializer principal pour le salon (avec toutes les infos nécessaires)
# class SalonDetailSerializer(serializers.ModelSerializer):
#     coiffeuse = CoiffeuseSerializer(read_only=True)
#     images = SalonImageSerializer(many=True, read_only=True)
#     avis = AvisSerializer(many=True, read_only=True)
#     services = serializers.SerializerMethodField()
#     adresse = serializers.SerializerMethodField()
#     horaires = serializers.SerializerMethodField()
#     note_moyenne = serializers.SerializerMethodField()
#     nombre_avis = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon', 'nom_salon', 'slogan', 'a_propos', 'logo_salon',
#             'coiffeuse', 'adresse', 'horaires', 'note_moyenne', 'nombre_avis',
#             'images', 'avis', 'services'
#         ]
#
#     def get_services(self, obj):
#         # Récupérer les services liés à ce salon via la table de jointure
#         services = TblService.objects.filter(salon_service__salon=obj)
#         return ServiceDetailSerializer(services, many=True).data
#
#     def get_adresse(self, obj):
#         # Récupérer l'adresse de la coiffeuse
#         user = obj.coiffeuse.idTblUser
#         if user.adresse:
#             return f"{user.adresse.numero} {user.adresse.rue.nom_rue}, {user.adresse.rue.localite.commune}, {user.adresse.rue.localite.code_postal}"
#         return None
#
#     def get_horaires(self, obj):
#         # Récupérer les horaires formatés depuis TblHoraireCoiffeuse
#         horaires = obj.coiffeuse.horaires.all().order_by('jour')
#         if horaires:
#             jours = {
#                 0: "Mon", 1: "Tue", 2: "Wed",
#                 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"
#             }
#             formatte = []
#             for h in horaires:
#                 debut = h.heure_debut.strftime("%I:%M %p")
#                 fin = h.heure_fin.strftime("%I:%M %p")
#                 formatte.append(f"{debut} - {fin} / {jours[h.jour]}")
#             return ", ".join(formatte)
#         return "10:00 AM - 6:00 PM / Mon - Fri"  # Valeur par défaut
#
#     def get_note_moyenne(self, obj):
#         # Calculer la note moyenne des avis
#         avis = obj.avis.all()
#         if avis:
#             return round(sum(a.note for a in avis) / len(avis), 1)
#         return 0
#
#     def get_nombre_avis(self, obj):
#         # Compter le nombre d'avis
#         return obj.avis.count()