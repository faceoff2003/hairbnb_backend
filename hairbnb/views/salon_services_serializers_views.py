from datetime import datetime

from django.utils.timezone import make_aware
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from hairbnb.business.business_logic import ServiceData, SalonData
from hairbnb.models import TblService, TblSalonService, TblSalon, TblTemps, TblPrix, TblServicePrix, \
    TblServiceTemps, TblPromotion, TblCoiffeuse, TblCoiffeuseSalon


@api_view(['GET'])
def get_services_by_coiffeuse(request, coiffeuse_id):
    try:
        coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
        salon_relation = TblCoiffeuseSalon.objects.filter(
            coiffeuse=coiffeuse,
            est_proprietaire=True
        ).first()
        salon = salon_relation.salon

        # Liste triée des services (via la table de jonction)
        salon_services_qs = TblSalonService.objects.filter(salon=salon).order_by('service__intitule_service')

        # Vérifie si pagination activée
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        if page and page_size:
            paginator = PageNumberPagination()
            paginator.page_size = int(page_size)
            result_page = paginator.paginate_queryset(salon_services_qs, request)

            # Sérialisation uniquement des services paginés
            salon_data = SalonData(salon, filtered_services=result_page).to_dict()

            return paginator.get_paginated_response({
                "status": "success",
                "salon": salon_data
            })
        else:
            # Retourne tous les services sans pagination
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


@api_view(['POST'])
def create_promotion(request, service_id):
    try:
        print("📥 Données reçues :", request.data)  # 🔥 DEBUG
        service = TblService.objects.get(idTblService=service_id)

        # Récupérer les données de la nouvelle promotion
        discount_percentage = request.data.get("discount_percentage")
        start_date_str = request.data.get("start_date")
        end_date_str = request.data.get("end_date")

        # Vérifier que les champs sont bien remplis
        if not discount_percentage or not end_date_str:
            return Response({"error": "Le pourcentage et la date de fin sont obligatoires."}, status=400)

        # Conversion des dates
        start_date = make_aware(datetime.strptime(start_date_str.split("T")[0], "%Y-%m-%d"))
        end_date = make_aware(datetime.strptime(end_date_str.split("T")[0], "%Y-%m-%d"))

        # Vérifier s'il existe déjà une promotion qui chevauche cette période
        existing_promotions = TblPromotion.objects.filter(service=service)

        # Une promotion chevauche si:
        # - Sa date de début est <= à la date de fin de la nouvelle promo ET
        # - Sa date de fin est >= à la date de début de la nouvelle promo
        overlapping_promotions = existing_promotions.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        if overlapping_promotions.exists():
            return Response({
                "error": "Il existe déjà une promotion active durant cette période. Veuillez choisir des dates qui ne chevauchent pas d'autres promotions."
            }, status=400)

        print(f"📝 Promotion reçue: {discount_percentage}% | Début: {start_date} | Fin: {end_date}")  # 🔥 DEBUG

        # Créer la promotion
        promotion = TblPromotion.objects.create(
            service=service,
            discount_percentage=float(discount_percentage),
            start_date=start_date,
            end_date=end_date
        )
        service_data = ServiceData(service).to_dict()
        return Response({"message": "Promotion créée avec succès.", "service": service_data}, status=201)
    except TblService.DoesNotExist:
        return Response({"error": "Service introuvable."}, status=404)
    except Exception as e:
        print("❌ Erreur interne:", str(e))  # 🔥 DEBUG
        return Response({"error": str(e)}, status=500)
