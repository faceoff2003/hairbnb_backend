# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import TblUser, TblCoiffeuse, TblSalon, TblService, TblSalonService, TblPrix, TblTemps, \
    TblServicePrix, TblServiceTemps, TblCoiffeuseSalon
from hairbnb.salon_services.salon_services_serializers import ServiceCreateSerializer, ServiceResponseSerializer




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

# @api_view(['POST'])
# @firebase_authenticated
# @is_owner(param_name="userId")
# def add_service_to_salon(request):
#     """
#     Ajouter un nouveau service au salon d'une coiffeuse.
#     Requiert que l'utilisateur soit authentifié via Firebase et soit propriétaire de l'ID fourni.
#     """
#     serializer = ServiceCreateSerializer(data=request.data)
#
#     if not serializer.is_valid():
#         return Response(
#             {"status": "error", "message": "Données invalides", "errors": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # Extraire les données validées
#     user_id = serializer.validated_data['userId']
#     service_name = serializer.validated_data['intitule_service']
#     service_description = serializer.validated_data['description']
#     prix = serializer.validated_data['prix']
#     temps_minutes = serializer.validated_data['temps_minutes']
#
#     try:
#         # Vérifier si l'utilisateur existe et est une coiffeuse
#         user = TblUser.objects.get(idTblUser=user_id)
#
#         #----------------------------------------------------------------------------------------------------------------------
#         # Logs de debugging
#         print(f"DEBUG: ID utilisateur reçu: {user_id}")
#         print(f"DEBUG: Utilisateur authentifié: {request.user.idTblUser}")
#         # ----------------------------------------------------------------------------------------------------------------------
#
#         # Vérification que l'utilisateur est une coiffeuse via le modèle TblType
#         if user.type_ref and user.type_ref.libelle != 'Coiffeuse':
#             return Response(
#                 {"status": "error", "message": "L'utilisateur n'est pas une coiffeuse"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         # Récupérer la coiffeuse liée à cet utilisateur
#         try:
#             coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
#         except TblCoiffeuse.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": "Profil de coiffeuse non trouvé"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Vérifier si la coiffeuse a un salon
#         try:
#             salon = TblSalon.objects.get(coiffeuse=coiffeuse)
#         except TblSalon.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": "Vous n'avez pas encore de salon enregistré"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Créer ou récupérer le service
#         service, service_created = TblService.objects.get_or_create(
#             intitule_service=service_name,
#             defaults={"description": service_description}
#         )
#
#         if not service_created and service.description != service_description:
#             # Mettre à jour la description si le service existe déjà mais avec une description différente
#             service.description = service_description
#             service.save()
#
#         # Associer le service au salon
#         salon_service, salon_service_created = TblSalonService.objects.get_or_create(
#             salon=salon,
#             service=service
#         )
#
#         # Créer ou récupérer le prix et le temps
#         prix_obj, prix_created = TblPrix.objects.get_or_create(prix=prix)
#         temps_obj, temps_created = TblTemps.objects.get_or_create(minutes=temps_minutes)
#
#         # Associer le service au prix (remplacer s'il existe déjà)
#         TblServicePrix.objects.update_or_create(
#             service=service,
#             defaults={"prix": prix_obj}
#         )
#
#         # Associer le service au temps
#         TblServiceTemps.objects.update_or_create(
#             service=service,
#             temps=temps_obj
#         )
#
#         # Sérialiser la réponse
#         response_serializer = ServiceResponseSerializer(service)
#
#         return Response({
#             "status": "success",
#             "message": "Service ajouté au salon avec succès",
#             "service": response_serializer.data,
#             "salon_id": salon.idTblSalon
#         }, status=status.HTTP_201_CREATED)
#
#     except TblUser.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Utilisateur non trouvé"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return Response(
#             {"status": "error", "message": f"Une erreur s'est produite: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#




# # views.py
#
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from hairbnb.models import TblUser, TblCoiffeuse, TblSalon, TblService, TblSalonService, TblPrix, TblTemps, \
#     TblServicePrix, TblServiceTemps
# from hairbnb.salon_services.salon_services_serializers import ServiceCreateSerializer, ServiceResponseSerializer
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_service_to_salon(request):
#     """
#     Ajouter un nouveau service au salon d'une coiffeuse.
#     Requiert que l'utilisateur soit authentifié et soit une coiffeuse avec un salon.
#     """
#     serializer = ServiceCreateSerializer(data=request.data)
#
#     if not serializer.is_valid():
#         return Response(
#             {"status": "error", "message": "Données invalides", "errors": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # Extraire les données validées
#     user_id = serializer.validated_data['userId']
#     service_name = serializer.validated_data['intitule_service']
#     service_description = serializer.validated_data['description']
#     prix = serializer.validated_data['prix']
#     temps_minutes = serializer.validated_data['temps_minutes']
#
#     try:
#         # Vérifier si l'utilisateur existe et est une coiffeuse
#         user = TblUser.objects.get(idTblUser=user_id)
#
#         # Vérification que l'utilisateur est une coiffeuse via le modèle TblType
#         if user.type_ref and user.type_ref.libelle != 'coiffeuse':
#             return Response(
#                 {"status": "error", "message": "L'utilisateur n'est pas une coiffeuse"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         # Récupérer la coiffeuse liée à cet utilisateur
#         try:
#             coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
#         except TblCoiffeuse.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": "Profil de coiffeuse non trouvé"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Vérifier si la coiffeuse a un salon
#         try:
#             salon = TblSalon.objects.get(coiffeuse=coiffeuse)
#         except TblSalon.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": "Vous n'avez pas encore de salon enregistré"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Créer ou récupérer le service
#         service, service_created = TblService.objects.get_or_create(
#             intitule_service=service_name,
#             defaults={"description": service_description}
#         )
#
#         if not service_created and service.description != service_description:
#             # Mettre à jour la description si le service existe déjà mais avec une description différente
#             service.description = service_description
#             service.save()
#
#         # Associer le service au salon
#         salon_service, salon_service_created = TblSalonService.objects.get_or_create(
#             salon=salon,
#             service=service
#         )
#
#         # Créer ou récupérer le prix et le temps
#         prix_obj, prix_created = TblPrix.objects.get_or_create(prix=prix)
#         temps_obj, temps_created = TblTemps.objects.get_or_create(minutes=temps_minutes)
#
#         # Associer le service au prix (remplacer s'il existe déjà)
#         TblServicePrix.objects.update_or_create(
#             service=service,
#             defaults={"prix": prix_obj}
#         )
#
#         # Associer le service au temps
#         TblServiceTemps.objects.update_or_create(
#             service=service,
#             temps=temps_obj
#         )
#
#         # Sérialiser la réponse
#         response_serializer = ServiceResponseSerializer(service)
#
#         return Response({
#             "status": "success",
#             "message": "Service ajouté au salon avec succès",
#             "service": response_serializer.data,
#             "salon_id": salon.idTblSalon
#         }, status=status.HTTP_201_CREATED)
#
#     except TblUser.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Utilisateur non trouvé"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return Response(
#             {"status": "error", "message": f"Une erreur s'est produite: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )