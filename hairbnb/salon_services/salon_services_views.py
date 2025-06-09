# views.py
from django.core.cache import cache
from django.db.models import Q
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status, serializers
from decimal import Decimal
from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import TblUser, TblCoiffeuse, TblSalon, TblService, TblSalonService, TblPrix, TblTemps, \
    TblServicePrix, TblServiceTemps, TblCoiffeuseSalon, TblPromotion
from hairbnb.salon.salon_business_logic import SalonData
from hairbnb.salon.salon_serializers import ServiceDropdownSerializer
from hairbnb.salon_services.category_services.category_serializers import ServiceWithCategorySerializer
from hairbnb.salon_services.salon_services_serializers import ServiceCreateSerializer, ServiceResponseSerializer, \
    AddExistingServiceSerializer, AddExistingServiceResponseSerializer, SalonServicesListResponseSerializer, \
    SalonServiceSerializer, ServiceUpdateSerializer


@api_view(['POST'])
@firebase_authenticated
@is_owner(param_name="userId")
def add_service_to_salon(request):
    """
    Ajouter un nouveau service au salon d'une coiffeuse.
    """
    serializer = ServiceCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": "Données invalides", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Extraire les données validées
    user_id = serializer.validated_data['userId']
    service_name = serializer.validated_data['intitule_service']
    service_description = serializer.validated_data['description']
    prix = serializer.validated_data['prix']
    temps_minutes = serializer.validated_data['temps_minutes']

    try:
        # Vérifier si l'utilisateur existe et est une coiffeuse
        user = TblUser.objects.get(idTblUser=user_id)

        # Vérification que l'utilisateur est une coiffeuse via le modèle TblType
        if user.type_ref and user.type_ref.libelle != 'Coiffeuse':
            return Response(
                {"status": "error", "message": "L'utilisateur n'est pas une coiffeuse"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Récupérer la coiffeuse liée à cet utilisateur
        try:
            coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
        except TblCoiffeuse.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profil de coiffeuse non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ⚠️ IMPORTANT: Rechercher le salon via la relation ManyToMany
        # Utiliser la table de jonction TblCoiffeuseSalon
        try:
            # Chercher un salon où cette coiffeuse est propriétaire
            coiffeuse_salon = TblCoiffeuseSalon.objects.filter(
                coiffeuse=coiffeuse,
                est_proprietaire=True
            ).first()

            if not coiffeuse_salon:
                return Response(
                    {"status": "error", "message": "Vous n'êtes pas propriétaire d'un salon"},
                    status=status.HTTP_404_NOT_FOUND
                )

            salon = coiffeuse_salon.salon
        except Exception as e:
            print(f"DEBUG: Erreur recherche salon: {str(e)}")
            return Response(
                {"status": "error", "message": "Impossible de trouver votre salon"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Créer ou récupérer le service
        service, service_created = TblService.objects.get_or_create(
            intitule_service=service_name,
            defaults={"description": service_description}
        )

        if not service_created and service.description != service_description:
            # Mettre à jour la description si le service existe déjà mais avec une description différente
            service.description = service_description
            service.save()

        # Associer le service au salon
        salon_service, salon_service_created = TblSalonService.objects.get_or_create(
            salon=salon,
            service=service
        )

        # Créer ou récupérer le prix et le temps
        prix_obj, prix_created = TblPrix.objects.get_or_create(prix=prix)
        temps_obj, temps_created = TblTemps.objects.get_or_create(minutes=temps_minutes)

        # Associer le service au prix (remplacer s'il existe déjà)
        TblServicePrix.objects.update_or_create(
            service=service,
            defaults={"prix": prix_obj}
        )

        # Associer le service au temps
        TblServiceTemps.objects.update_or_create(
            service=service,
            temps=temps_obj
        )

        # Utiliser le serializer pour la réponse
        response_serializer = ServiceResponseSerializer(service)

        return Response({
            "status": "success",
            "message": "Service ajouté au salon avec succès",
            "service": response_serializer.data,
            "salon_id": salon.idTblSalon
        }, status=status.HTTP_201_CREATED)

    except TblUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "Utilisateur non trouvé"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        print(f"ERREUR COMPLETE: {str(e)}")
        print(traceback.format_exc())

        return Response(
            {"status": "error", "message": f"Une erreur s'est produite: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@firebase_authenticated
@is_owner(param_name="userId")
def add_existing_service_to_salon(request):
    """
    Associe un service existant à un salon avec prix et durée personnalisés.
    Utilise des serializers pour la validation et la réponse.
    """
    try:
        # VALIDATION avec serializer
        serializer = AddExistingServiceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Données invalides",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # RÉCUPÉRATION des données validées
        validated_data = serializer.validated_data
        user_id = validated_data['userId']
        service_id = validated_data['service_id']
        prix = validated_data['prix']
        temps_minutes = validated_data['temps_minutes']

        # RÉCUPÉRATION de l'utilisateur
        user = TblUser.objects.get(idTblUser=user_id)

        # RÉCUPÉRATION de la coiffeuse et son salon
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

        # RÉCUPÉRATION du service (déjà validé par le serializer)
        service = TblService.objects.get(idTblService=service_id)

        # VÉRIFICATION : Service déjà associé à CE salon
        if TblSalonService.objects.filter(salon=salon, service=service).exists():
            return Response({
                "status": "error",
                "message": f"Le service '{service.intitule_service}' est déjà proposé par votre salon"
            }, status=status.HTTP_400_BAD_REQUEST)

        # CRÉATION : Prix et temps
        prix_obj, _ = TblPrix.objects.get_or_create(prix=prix)
        temps_obj, _ = TblTemps.objects.get_or_create(minutes=temps_minutes)

        # ASSOCIATION : Service au salon
        salon_service = TblSalonService.objects.create(
            salon=salon,
            service=service
        )

        # LIAISON : Service + Prix + Salon
        service_prix = TblServicePrix.objects.create(
            service=service,
            prix=prix_obj,
            salon=salon
        )

        # LIAISON : Service + Temps + Salon
        service_temps = TblServiceTemps.objects.create(
            service=service,
            temps=temps_obj,
            salon=salon
        )

        # RÉPONSE avec serializer
        response_data = {
            "status": "success",
            "message": "Service existant ajouté au salon avec succès",
            "service": {
                "id": service.idTblService,
                "intitule": service.intitule_service,
                "description": service.description
            },
            "salon_id": salon.idTblSalon,
            "salon_nom": salon.nom_salon,
            "prix": float(prix),
            "duree_minutes": temps_minutes
        }

        # VALIDATION de la réponse avec serializer
        response_serializer = AddExistingServiceResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            # Fallback si problème avec le serializer de réponse
            return Response(response_data, status=status.HTTP_201_CREATED)

    except TblUser.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Utilisateur non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except TblCoiffeuse.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Profil de coiffeuse non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_global_services(request):
    """
    Recherche les services globaux existants par nom ou description.
    Permet au frontend de proposer des services existants avant d'en créer de nouveaux.

    Query params:
    - q: terme de recherche
    - limit: nombre max de résultats (défaut: 10)
    """
    try:
        search_term = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 50)

        if len(search_term) < 2:
            return Response({
                "status": "error",
                "message": "Le terme de recherche doit contenir au moins 2 caractères"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Recherche dans les noms et descriptions
        services = TblService.objects.filter(
            Q(intitule_service__icontains=search_term) |
            Q(description__icontains=search_term)
        )[:limit]

        # Ajouter des infos sur les prix/durées moyens ou les plus fréquents
        services_data = []
        for service in services:
            # Récupérer les prix les plus fréquents pour ce service
            prix_populaires = TblServicePrix.objects.filter(
                service=service
            ).select_related('prix').values(
                'prix__prix'
            ).distinct()[:3]

            # Récupérer les durées les plus fréquentes
            durees_populaires = TblServiceTemps.objects.filter(
                service=service
            ).select_related('temps').values(
                'temps__minutes'
            ).distinct()[:3]

            service_data = ServiceResponseSerializer(service).data
            service_data['prix_populaires'] = [p['prix__prix'] for p in prix_populaires]
            service_data['durees_populaires'] = [d['temps__minutes'] for d in durees_populaires]
            service_data['nb_salons_utilisant'] = TblSalonService.objects.filter(service=service).count()

            services_data.append(service_data)

        return Response({
            "status": "success",
            "message": f"{len(services_data)} services trouvés",
            "services": services_data,
            "search_term": search_term
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur lors de la recherche: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@firebase_authenticated
def get_salon_services(request, salon_id):
    """
    Récupère tous les services proposés par un salon spécifique.
    Utilise des serializers pour la réponse.
    """
    try:
        # Récupérer le salon
        salon = TblSalon.objects.get(idTblSalon=salon_id)

        # Récupérer tous les services du salon
        salon_services = TblSalonService.objects.filter(salon=salon).select_related('service')

        # ✅ SÉRIALISATION avec serializer
        serializer = SalonServiceSerializer(salon_services, many=True)

        response_data = {
            "status": "success",
            "services": serializer.data,
            "total": len(serializer.data)
        }

        # ✅ VALIDATION de la réponse
        response_serializer = SalonServicesListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=status.HTTP_200_OK)

    except TblSalon.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Salon non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@firebase_authenticated
@is_owner(param_name="userId")
def remove_service_from_salon(request, salon_service_id):
    """
    Retire un service d'un salon (ne supprime pas le service global).
    """
    try:
        user_id = request.data.get('userId') or request.GET.get('userId')

        # Vérifications utilisateur/salon habituelles...
        user = TblUser.objects.get(idTblUser=user_id)
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
        coiffeuse_salon = TblCoiffeuseSalon.objects.filter(
            coiffeuse=coiffeuse,
            est_proprietaire=True
        ).first()

        if not coiffeuse_salon:
            return Response({
                "status": "error",
                "message": "Salon non trouvé"
            }, status=status.HTTP_404_NOT_FOUND)

        salon = coiffeuse_salon.salon

        # Récupérer et supprimer la relation salon-service
        try:
            salon_service = TblSalonService.objects.get(
                idSalonService=salon_service_id,
                salon=salon
            )
            service = salon_service.service
            salon_service.delete()

            # Optionnel : Nettoyer les prix/durées si plus aucun salon n'utilise ce service
            if not TblSalonService.objects.filter(service=service).exists():
                TblServicePrix.objects.filter(service=service).delete()
                TblServiceTemps.objects.filter(service=service).delete()
                # Note: on peut choisir de garder le service global pour réutilisation future

            return Response({
                "status": "success",
                "message": "Service retiré du salon avec succès"
            }, status=status.HTTP_200_OK)

        except TblSalonService.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Service non trouvé dans ce salon"
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@firebase_authenticated
def services_dropdown_list(request):
    """
    Vue optimisée pour les dropdowns Flutter.
    Retourne : ID service, nom service, ID catégorie, nom catégorie.
    """
    try:
        # Cache pour éviter les requêtes répétées
        cache_key = 'services_dropdown_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        # Requête optimisée avec select_related pour éviter N+1 queries
        services = TblService.objects.select_related('categorie').all()
        serializer = ServiceDropdownSerializer(services, many=True)

        response_data = {
            'status': 'success',
            'message': 'Services récupérés avec succès',
            'services': serializer.data,
            'count': services.count()
        }

        # Cache pendant 30 minutes
        cache.set(cache_key, response_data, 60 * 30)

        return Response(response_data)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        }, status=500)


# View mise à jour avec décorateurs et logique dans le serializer
@api_view(['PUT'])
@firebase_authenticated
@is_owner(param_name="userId")
def update_service(request, service_id):
    """
    Met à jour le prix et/ou le temps d'un service.

    Paramètres:
    - service_id: ID du service à modifier
    - userId: ID de l'utilisateur (coiffeuse propriétaire)
    - prix (optionnel): Nouveau prix du service
    - temps_minutes (optionnel): Nouvelle durée en minutes

    Réponse:
    - Confirmation de la mise à jour
    """
    serializer = ServiceUpdateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Données invalides",
            "errors": serializer.errors
        }, status=400)

    try:
        # La logique métier est dans le serializer
        service = serializer.update_service(service_id, serializer.validated_data)

        return Response({
            "status": "success",
            "message": "Service mis à jour avec succès",
            "service_id": service.idTblService,
            "service_name": service.intitule_service
        }, status=200)

    except serializers.ValidationError as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }, status=500)


@api_view(['GET'])
@firebase_authenticated
def get_salon_services_by_salon_id(request, salon_id):
    """
    Récupère tous les services d'un salon organisés par catégorie.
    AVEC les promotions spécifiques au salon ! 🎯

    Params:
    - salon_id: ID du salon
    """
    try:
        # Récupérer le salon
        try:
            salon = TblSalon.objects.get(idTblSalon=salon_id)
        except TblSalon.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Salon non trouvé"
            }, status=status.HTTP_404_NOT_FOUND)

        # Récupérer tous les services du salon avec leurs catégories
        salon_services = TblSalonService.objects.filter(
            salon=salon
        ).select_related('service__categorie')

        # Organiser par catégorie
        services_by_category = {}
        for salon_service in salon_services:
            service = salon_service.service
            category_name = service.categorie.intitule_categorie if service.categorie else "Sans catégorie"

            if category_name not in services_by_category:
                services_by_category[category_name] = {
                    "category_id": service.categorie.idTblCategorie if service.categorie else None,
                    "category_name": category_name,
                    "services": []
                }

            # Récupérer prix et durée pour ce service dans ce salon
            service_prix = TblServicePrix.objects.filter(
                service=service,
                salon=salon
            ).first()

            service_temps = TblServiceTemps.objects.filter(
                service=service,
                salon=salon  # ✅ Spécifique au salon
            ).first()

            # ✅ RÉCUPÉRER LES PROMOTIONS SPÉCIFIQUES AU SALON
            promotion_active = TblPromotion.objects.filter(
                service=service,
                salon=salon,
                start_date__lte=now(),
                end_date__gte=now()
            ).first()

            # Calcul du prix final avec promotion
            prix_original = service_prix.prix.prix if service_prix else Decimal("0.00")
            prix_final = prix_original

            promotion_data = None
            if promotion_active and promotion_active.is_active():
                prix_final = promotion_active.get_prix_avec_promotion(prix_original)
                promotion_data = {
                    "id": promotion_active.idPromotion,
                    "pourcentage": float(promotion_active.discount_percentage),
                    "prix_original": float(prix_original),
                    "prix_final": float(prix_final),
                    "economie": float(promotion_active.get_montant_economise(prix_original)),
                    "date_fin": promotion_active.end_date.isoformat(),
                    "est_active": True
                }

            # Construire les données du service
            service_data = ServiceWithCategorySerializer(service).data
            service_data.update({
                'salon_service_id': salon_service.idSalonService,
                'prix': float(prix_original),
                'prix_final': float(prix_final),
                'duree_minutes': service_temps.temps.minutes if service_temps else None,
                'promotion': promotion_data
            })

            services_by_category[category_name]["services"].append(service_data)

        return Response({
            "status": "success",
            "message": "Services du salon récupérés par catégorie avec promotions",
            "salon_id": salon.idTblSalon,
            "salon_name": salon.nom_salon,
            "services_by_category": list(services_by_category.values()),
            "total_services": salon_services.count()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
#@firebase_authenticated
def get_services_by_coiffeuse(request, coiffeuse_id):
    """
    Récupère les services d'un salon appartenant à une coiffeuse spécifique.

    Paramètres:
    - coiffeuse_id: ID de la coiffeuse propriétaire du salon
    - page (optionnel): Numéro de page pour la pagination
    - page_size (optionnel): Nombre d'éléments par page

    Réponse:
    - Informations du salon avec ses services (incluant les catégories)
    - Support de la pagination si page et page_size sont fournis
    """
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

    except TblCoiffeuse.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Coiffeuse non trouvée."
        }, status=404)
    except TblSalon.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Aucun salon trouvé pour cette coiffeuse."
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }, status=500)