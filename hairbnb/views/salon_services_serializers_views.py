from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hairbnb.models import TblService, TblSalonService, TblCoiffeuse, TblSalon, TblTemps, TblPrix, TblServicePrix, TblServiceTemps
from hairbnb.business.business_logic import ServiceData, SalonData, FullSalonServiceData
from hairbnb.serializers.salon_services_serializers import ServiceSerializer


# ✅ Récupérer tous les services d'une coiffeuse via son salon

@api_view(['GET'])
def get_services_by_coiffeuse(request, coiffeuse_id):
    try:
        salon_services = TblSalonService.objects.filter(salon__coiffeuse__idTblUser=coiffeuse_id).select_related(
            'salon', 'service', 'salon__coiffeuse')
        services_data = [FullSalonServiceData(salon_service).to_dict() for salon_service in salon_services]

        return Response({"status": "success", "services": services_data}, status=200)

    except TblSalonService.DoesNotExist:
        return Response({"status": "error", "message": "Aucun service trouvé pour cette coiffeuse."}, status=404)

# @api_view(['GET'])
# def get_services_by_coiffeuse(request, coiffeuse_id):
#     try:
#         salon = TblSalon.objects.get(coiffeuse__idTblUser=coiffeuse_id)
#         salon_data = SalonData(salon).to_dict()
#         return Response({"status": "success", "salon": salon_data}, status=200)
#
#     except TblSalon.DoesNotExist:
#         return Response({"status": "error", "message": "Aucun salon trouvé pour cette coiffeuse."}, status=404)


# ✅ Ajouter un service à une coiffeuse

@api_view(['POST'])
def add_service_to_salon(request):
    try:
        salon_id = request.data.get('idTblSalon')
        service_data = request.data.get('service')

        # Validation des données
        if not salon_id or not service_data:
            return Response({"status": "error", "message": "Données invalides."}, status=400)

        # Récupération du salon
        salon = TblSalon.objects.get(idTblSalon=salon_id)

        # Création du service
        service_serializer = ServiceSerializer(data=service_data)
        if service_serializer.is_valid():
            service = service_serializer.save()
            TblSalonService.objects.create(salon=salon, service=service)

            return Response({"status": "success", "message": "Service ajouté avec succès."}, status=201)
        else:
            return Response({"status": "error", "errors": service_serializer.errors}, status=400)

    except TblSalon.DoesNotExist:
        return Response({"status": "error", "message": "Salon introuvable."}, status=404)


# @api_view(['POST'])
# def add_service_to_coiffeuse(request, coiffeuse_id):
#     try:
#         salon = TblSalon.objects.get(coiffeuse__idTblUser=coiffeuse_id)
#
#         # Extraire les données
#         temps_minutes = request.data.pop('temps', None)
#         prix_montant = request.data.pop('prix', None)
#
#         service = TblService.objects.create(**request.data)
#
#         # Associer Temps et Prix
#         if temps_minutes:
#             temps, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)
#             TblServiceTemps.objects.create(service=service, temps=temps)
#
#         if prix_montant:
#             prix, _ = TblPrix.objects.get_or_create(prix=prix_montant)
#             TblServicePrix.objects.create(service=service, prix=prix)
#
#         # Lier au salon
#         TblSalonService.objects.create(salon=salon, service=service)
#
#         return Response({"status": "success", "message": "Service ajouté avec succès."}, status=201)
#
#     except TblSalon.DoesNotExist:
#         return Response({"status": "error", "message": "Aucun salon trouvé pour cette coiffeuse."}, status=404)


# ✅ Modifier un service
@api_view(['PUT'])
def update_service(request, service_id):
    try:
        service = TblService.objects.get(idTblService=service_id)

        # Extraire le temps et le prix
        temps_minutes = request.data.pop('temps', None)
        prix_montant = request.data.pop('prix', None)

        for key, value in request.data.items():
            setattr(service, key, value)
        service.save()

        # Mettre à jour le temps et le prix
        if temps_minutes:
            temps, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)
            TblServiceTemps.objects.update_or_create(service=service, defaults={'temps': temps})

        if prix_montant:
            prix, _ = TblPrix.objects.get_or_create(prix=prix_montant)
            TblServicePrix.objects.update_or_create(service=service, defaults={'prix': prix})

        return Response({"status": "success", "message": "Service mis à jour."}, status=200)

    except TblService.DoesNotExist:
        return Response({"status": "error", "message": "Service introuvable."}, status=404)


# ✅ Supprimer un service
@api_view(['DELETE'])
def delete_service_from_salon(request, salon_id, service_id):
    try:
        salon_service = TblSalonService.objects.get(salon__idTblSalon=salon_id, service__idTblService=service_id)
        salon_service.delete()
        return Response({"status": "success", "message": "Service supprimé avec succès."}, status=200)

    except TblSalonService.DoesNotExist:
        return Response({"status": "error", "message": "Service non trouvé pour ce salon."}, status=404)

