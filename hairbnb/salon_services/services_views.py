# services_views.py - Nouvelles vues pour gérer la logique correcte des services

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import (
    TblUser, TblCoiffeuse, TblService, TblSalonService,
    TblPrix, TblTemps, TblServicePrix, TblServiceTemps, TblCoiffeuseSalon, TblCategorie
)
from hairbnb.salon_services.salon_services_serializers import (
    ServiceResponseSerializer, ServiceCreateSerializer
)


@api_view(['GET'])
def get_all_services(request):
    """
    Récupère tous les services globaux existants avec leurs prix/durées moyens.
    """
    try:
        services = TblService.objects.all()
        serializer = ServiceResponseSerializer(services, many=True)

        return Response({
            "status": "success",
            "message": "Services récupérés avec succès",
            "services": serializer.data,
            "count": services.count()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur lors de la récupération des services: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@firebase_authenticated
@is_owner(param_name="userId")
def create_new_global_service(request):
    """
    Crée un nouveau service global ET l'associe au salon de la coiffeuse.
    Body attendu:
    {
        "userId": int,
        "intitule_service": str,
        "description": str,
        "prix": float,
        "temps_minutes": int,
        "categorie_id": int (obligatoire)
    }
    """
    serializer = ServiceCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Données invalides",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Extraire les données validées
        user_id = serializer.validated_data['userId']
        service_name = serializer.validated_data['intitule_service']
        service_description = serializer.validated_data['description']
        prix = serializer.validated_data['prix']
        temps_minutes = serializer.validated_data['temps_minutes']
        categorie_id = serializer.validated_data['categorie_id']  # ✅ AJOUTÉ

        # ✅ Récupérer la catégorie
        try:
            categorie = TblCategorie.objects.get(idTblCategorie=categorie_id)
        except TblCategorie.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Catégorie non trouvée"
            }, status=status.HTTP_404_NOT_FOUND)

        # Récupérer l'utilisateur et vérifier qu'il est une coiffeuse
        user = TblUser.objects.get(idTblUser=user_id)
        if user.type_ref.libelle != 'Coiffeuse':
            return Response({
                "status": "error",
                "message": "L'utilisateur n'est pas une coiffeuse"
            }, status=status.HTTP_403_FORBIDDEN)
        # Récupérer la coiffeuse et son salon
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
        coiffeuse_salon = TblCoiffeuseSalon.objects.filter(
            coiffeuse=coiffeuse,
            est_proprietaire=True
        ).first()
        if not coiffeuse_salon:
            return Response({
                "status": "error",
                "message": "Vous n'êtes pas propriétaire d'un salon"
            }, status=status.HTTP_404_NOT_FOUND)
        salon = coiffeuse_salon.salon

        # Vérifier si un service avec ce nom existe déjà
        if TblService.objects.filter(intitule_service__iexact=service_name).exists():
            return Response({
                "status": "error",
                "message": f"Un service nommé '{service_name}' existe déjà. Utilisez plutôt 'Ajouter un service existant'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Créer le nouveau service global AVEC catégorie
        service = TblService.objects.create(
            intitule_service=service_name,
            description=service_description,
            categorie=categorie
        )

        # Créer ou récupérer le prix et le temps
        prix_obj, _ = TblPrix.objects.get_or_create(prix=prix)
        temps_obj, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)

        # Associer le service au salon
        salon_service = TblSalonService.objects.create(
            salon=salon,
            service=service
        )

        # Créer les relations prix et temps
        TblServicePrix.objects.create(
            service=service,
            prix=prix_obj,
            salon=salon
        )
        TblServiceTemps.objects.create(
            service=service,
            temps=temps_obj,
            salon=salon
        )

        return Response({
            "status": "success",
            "message": "Nouveau service créé et ajouté au salon avec succès",
            "service": ServiceResponseSerializer(service).data,
            "salon_id": salon.idTblSalon,
            "is_new_service": True
        }, status=status.HTTP_201_CREATED)

    except TblUser.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Utilisateur non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)