# serializers.py
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated
from hairbnb.models import TblService, TblSalonService, TblServicePrix, TblServiceTemps, TblSalon, TblCoiffeuse, \
    TblCoiffeuseSalon
from hairbnb.salon.salon_business_logic import SalonData


# @api_view(['GET'])
# #@firebase_authenticated
# def get_services_by_coiffeuse(request, coiffeuse_id):
#     """
#     Récupère les services d'un salon appartenant à une coiffeuse spécifique.
#
#     Paramètres:
#     - coiffeuse_id: ID de la coiffeuse propriétaire du salon
#     - page (optionnel): Numéro de page pour la pagination
#     - page_size (optionnel): Nombre d'éléments par page
#
#     Réponse:
#     - Informations du salon avec ses services (incluant les catégories)
#     - Support de la pagination si page et page_size sont fournis
#     """
#     try:
#         coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
#         salon_relation = TblCoiffeuseSalon.objects.filter(
#             coiffeuse=coiffeuse,
#             est_proprietaire=True
#         ).first()
#         salon = salon_relation.salon
#
#         # Liste triée des services (via la table de jonction)
#         salon_services_qs = TblSalonService.objects.filter(salon=salon).order_by('service__intitule_service')
#
#         # Vérifie si pagination activée
#         page = request.GET.get('page')
#         page_size = request.GET.get('page_size')
#
#         if page and page_size:
#             paginator = PageNumberPagination()
#             paginator.page_size = int(page_size)
#             result_page = paginator.paginate_queryset(salon_services_qs, request)
#
#             # Sérialisation uniquement des services paginés
#             salon_data = SalonData(salon, filtered_services=result_page).to_dict()
#
#             return paginator.get_paginated_response({
#                 "status": "success",
#                 "salon": salon_data
#             })
#         else:
#             # Retourne tous les services sans pagination
#             salon_data = SalonData(salon).to_dict()
#             return Response({"status": "success", "salon": salon_data}, status=200)
#
#     except TblCoiffeuse.DoesNotExist:
#         return Response({
#             "status": "error",
#             "message": "Coiffeuse non trouvée."
#         }, status=404)
#     except TblSalon.DoesNotExist:
#         return Response({
#             "status": "error",
#             "message": "Aucun salon trouvé pour cette coiffeuse."
#         }, status=404)
#     except Exception as e:
#         return Response({
#             "status": "error",
#             "message": f"Erreur serveur: {str(e)}"
#         }, status=500)


class ServiceCreateSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    intitule_service = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    prix = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    temps_minutes = serializers.IntegerField(required=True)
    categorie_id = serializers.IntegerField(required=True)

    class Meta:
        fields = ['userId', 'intitule_service', 'description', 'prix', 'temps_minutes', 'categorie_id']


# ✅ Serializer pour ajouter un service existant à un salon
class AddExistingServiceSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    service_id = serializers.IntegerField(required=True)
    prix = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    temps_minutes = serializers.IntegerField(required=True)

    def validate_userId(self, value):
        """Valide que l'utilisateur existe et est une coiffeuse"""
        from hairbnb.models import TblUser
        try:
            user = TblUser.objects.get(idTblUser=value)
            if user.type_ref.libelle != 'Coiffeuse':
                raise serializers.ValidationError("L'utilisateur n'est pas une coiffeuse")
            return value
        except TblUser.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé")

    def validate_service_id(self, value):
        """Valide que le service existe"""
        try:
            TblService.objects.get(idTblService=value)
            return value
        except TblService.DoesNotExist:
            raise serializers.ValidationError("Service non trouvé")

    def validate_prix(self, value):
        """Valide que le prix est positif"""
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0")
        return value

    def validate_temps_minutes(self, value):
        """Valide que le temps est positif"""
        if value <= 0:
            raise serializers.ValidationError("La durée doit être supérieure à 0")
        return value


# ✅ Serializer pour la réponse après ajout d'un service
class AddExistingServiceResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
    service = serializers.DictField()
    salon_id = serializers.IntegerField()
    salon_nom = serializers.CharField()
    prix = serializers.DecimalField(max_digits=5, decimal_places=2)
    duree_minutes = serializers.IntegerField()


# ✅ ServiceResponseSerializer pour prendre en compte le salon
class ServiceResponseSerializer(serializers.ModelSerializer):
    prix = serializers.SerializerMethodField()
    temps_minutes = serializers.SerializerMethodField()
    salon_nom = serializers.SerializerMethodField()

    class Meta:
        model = TblService
        fields = ['idTblService', 'intitule_service', 'description', 'prix', 'temps_minutes', 'salon_nom']

    def get_prix(self, obj):
        """Récupère le prix pour un salon spécifique si fourni dans le contexte"""
        salon_id = self.context.get('salon_id')
        if salon_id:
            service_prix = obj.service_prix.filter(salon_id=salon_id).first()
        else:
            service_prix = obj.service_prix.first()
        return float(service_prix.prix.prix) if service_prix else 0.0

    def get_temps_minutes(self, obj):
        """Récupère la durée pour un salon spécifique si fourni dans le contexte"""
        salon_id = self.context.get('salon_id')
        if salon_id:
            service_temps = obj.service_temps.filter(salon_id=salon_id).first()
        else:
            service_temps = obj.service_temps.first()
        return service_temps.temps.minutes if service_temps else 0

    def get_salon_nom(self, obj):
        """Récupère le nom du salon si fourni dans le contexte"""
        salon_id = self.context.get('salon_id')
        if salon_id:
            try:
                salon = TblSalon.objects.get(idTblSalon=salon_id)
                return salon.nom_salon
            except TblSalon.DoesNotExist:
                return None
        return None


# ✅ Serializer pour les services d'un salon spécifique
class SalonServiceSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(source='service.idTblService')
    intitule_service = serializers.CharField(source='service.intitule_service')
    description = serializers.CharField(source='service.description')
    prix = serializers.SerializerMethodField()
    duree_minutes = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source='service.categorie.idTblCategorie', allow_null=True)

    class Meta:
        model = TblSalonService
        fields = ['service_id', 'intitule_service', 'description', 'prix', 'duree_minutes', 'category_id']

    def get_prix(self, obj):
        """Récupère le prix de ce service dans ce salon"""
        service_prix = TblServicePrix.objects.filter(
            service=obj.service,
            salon=obj.salon
        ).first()
        return float(service_prix.prix.prix) if service_prix else 0.0

    def get_duree_minutes(self, obj):
        """Récupère la durée de ce service dans ce salon"""
        service_temps = TblServiceTemps.objects.filter(
            service=obj.service,
            salon=obj.salon
        ).first()
        return service_temps.temps.minutes if service_temps else 0


# ✅ Serializer pour lister les services d'un salon
class SalonServicesListResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    services = SalonServiceSerializer(many=True)
    total = serializers.IntegerField()


# ✅ Serializer pour mettre à jour un service
class ServiceUpdateSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    prix = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    temps_minutes = serializers.IntegerField(required=False)

    def validate_userId(self, value):
        """Valide que l'utilisateur existe et est une coiffeuse"""
        from hairbnb.models import TblUser
        try:
            user = TblUser.objects.get(idTblUser=value)
            if user.type_ref.libelle != 'Coiffeuse':
                raise serializers.ValidationError("L'utilisateur n'est pas une coiffeuse")
            return value
        except TblUser.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé")

    def validate_prix(self, value):
        """Valide que le prix est positif"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0")
        return value

    def validate_temps_minutes(self, value):
        """Valide que le temps est positif"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("La durée doit être supérieure à 0")
        return value

    def validate(self, attrs):
        """Validation globale - au moins un champ doit être fourni"""
        if not attrs.get('prix') and not attrs.get('temps_minutes'):
            raise serializers.ValidationError(
                "Au moins un champ (prix ou temps_minutes) doit être fourni pour la mise à jour"
            )
        return attrs

    def update_service(self, service_id, validated_data):
        """Met à jour le service avec les données validées"""
        from hairbnb.models import TblService, TblTemps, TblServiceTemps, TblPrix, TblServicePrix

        try:
            service = TblService.objects.get(idTblService=service_id)

            # Gestion du temps
            if 'temps_minutes' in validated_data:
                temps, _ = TblTemps.objects.get_or_create(minutes=validated_data['temps_minutes'])
                TblServiceTemps.objects.update_or_create(service=service, defaults={'temps': temps})

            # Gestion du prix
            if 'prix' in validated_data:
                prix_obj, _ = TblPrix.objects.get_or_create(prix=validated_data['prix'])
                TblServicePrix.objects.update_or_create(service=service, defaults={'prix': prix_obj})

            return service

        except TblService.DoesNotExist:
            raise serializers.ValidationError("Service introuvable")