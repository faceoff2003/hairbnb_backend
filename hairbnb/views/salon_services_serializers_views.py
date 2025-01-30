from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hairbnb.models import TblService, TblSalonService, TblCoiffeuse, TblSalon, TblTemps, TblPrix, TblServicePrix, TblServiceTemps
from hairbnb.business.business_logic import ServiceData, SalonData


# ✅ Récupérer tous les services d'une coiffeuse via son salon
@api_view(['GET'])
def get_services_by_coiffeuse(request, coiffeuse_id):
    try:
        salon = TblSalon.objects.get(coiffeuse__idTblUser=coiffeuse_id)
        salon_data = SalonData(salon).to_dict()
        return Response({"status": "success", "salon": salon_data}, status=200)

    except TblSalon.DoesNotExist:
        return Response({"status": "error", "message": "Aucun salon trouvé pour cette coiffeuse."}, status=404)


# ✅ Ajouter un service à une coiffeuse

@api_view(['POST'])
def add_service_to_coiffeuse(request, coiffeuse_id):
    print(f"🔍 Requête reçue pour coiffeuse_id: {coiffeuse_id}")
    print(f"📩 Données reçues: {request.data}")

    try:
        # Vérifier si la coiffeuse a un salon
        salon = TblSalon.objects.get(coiffeuse__idTblUser=coiffeuse_id)
        print(f"✅ Salon trouvé: {salon}")

        # Extraire les données
        intitule_service = request.data.get('intitule_service')
        description = request.data.get('description', '')
        temps_minutes = request.data.get('temps')
        prix_montant = request.data.get('prix')

        # Vérifier si les champs sont bien remplis
        if not intitule_service or not prix_montant or not temps_minutes:
            return Response({"status": "error", "message": "Champs manquants"}, status=400)

        # Créer le service
        service = TblService.objects.create(intitule_service=intitule_service, description=description)
        print(f"✅ Service ajouté: {service}")

        # Associer Temps
        temps, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)
        TblServiceTemps.objects.create(service=service, temps=temps)

        # 🔍 Vérifier si un prix existe déjà sans lever d'erreur
        prix = TblPrix.objects.filter(prix=prix_montant).first()

        # 🛠️ Si aucun prix trouvé, on le crée
        if not prix:
            prix = TblPrix.objects.create(prix=prix_montant)

        TblServicePrix.objects.create(service=service, prix=prix)

        # Lier au salon
        TblSalonService.objects.create(salon=salon, service=service)
        print("✅ Association Salon-Service créée.")

        return Response({"status": "success", "message": "Service ajouté avec succès."}, status=201)

    except TblSalon.DoesNotExist:
        print("❌ Erreur: Aucun salon trouvé pour cette coiffeuse.")
        return Response({"status": "error", "message": "Aucun salon trouvé pour cette coiffeuse."}, status=404)

    except Exception as e:
        print(f"❌ Erreur interne : {e}")
        return Response({"status": "error", "message": str(e)}, status=500)
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
        # ✅ Gestion du temps (évite les doublons)
        if temps_minutes:
            temps, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)
            TblServiceTemps.objects.update_or_create(service=service, defaults={'temps': temps})

        # ✅ Gestion du prix (évite les doublons)
        if prix_montant:
            prix_obj, created = TblPrix.objects.get_or_create(prix=prix_montant)
            TblServicePrix.objects.update_or_create(service=service, defaults={'prix': prix_obj})


        return Response({"status": "success", "message": "Service mis à jour."}, status=200)

    except TblService.DoesNotExist:
        return Response({"status": "error", "message": "Service introuvable."}, status=404)


# ✅ Supprimer un service
@api_view(['DELETE'])
def delete_service(request, service_id):
    try:
        service = TblService.objects.get(idTblService=service_id)
        service.delete()
        return Response({"status": "success", "message": "Service supprimé."}, status=200)

    except TblService.DoesNotExist:
        return Response({"status": "error", "message": "Service introuvable."}, status=404)
