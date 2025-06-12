import logging
import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import auth
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import (
    TblUser, TblCoiffeuse, TblAdresse, TblRue, TblLocalite, TblCoiffeuseSalon)
from hairbnb.profil.profil_serializers import UserSerializer, CoiffeuseSerializer, UserCreationSerializer, \
    DeleteProfileResponseSerializer, DeleteProfileUserSerializer


@csrf_exempt
@api_view(['GET'])
def get_user_profile(request, userUuid):
    try:
        # Récupérer l'utilisateur
        user = get_object_or_404(TblUser, uuid=userUuid)

        # Utiliser le serializer approprié
        user_serializer = UserSerializer(user)
        user_data = user_serializer.data

        # Ajouter l'adresse formatée pour plus de facilité d'utilisation côté client
        if user.adresse:
            user_data.update({
                "adresse_formatee": f"{user.adresse.numero}, {user.adresse.rue.nom_rue}",
                "code_postal": user.adresse.rue.localite.code_postal,
                "commune": user.adresse.rue.localite.commune,
            })

        # Vérifier si l'utilisateur est une coiffeuse et ajouter les informations professionnelles
        try:
            if hasattr(user, 'type_ref') and user.type_ref and user.type_ref.libelle == "coiffeuse" and hasattr(user,
                                                                                                                'coiffeuse'):
                coiffeuse_serializer = CoiffeuseSerializer(user.coiffeuse)
                # On ne garde que les informations professionnelles spécifiques
                pro_data = {
                    "nom_commercial": coiffeuse_serializer.data['nom_commercial'],
                }

                user_data.update({
                    "coiffeuse_data": pro_data
                })

                # Ajouter les informations des salons où travaille la coiffeuse
                salon_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=user.coiffeuse)
                if salon_relations.exists():
                    salons_data = []
                    salon_principal = None

                    for relation in salon_relations:
                        salon = relation.salon
                        salon_info = {
                            "idTblSalon": salon.idTblSalon,
                            "nom_salon": salon.nom_salon,
                            "position": salon.position,
                            "numero_tva": salon.numero_tva,  # TVA maintenant dans le salon
                            "est_proprietaire": relation.est_proprietaire
                        }

                        salons_data.append(salon_info)

                        # Identifier le salon principal (où la coiffeuse est propriétaire)
                        if relation.est_proprietaire:
                            salon_principal = salon_info

                    user_data["salons_data"] = salons_data
                    if salon_principal:
                        user_data["salon_principal"] = salon_principal

        except TblCoiffeuse.DoesNotExist:
            # Si l'utilisateur n'a pas d'entrée dans la table coiffeuse, on ne fait rien
            pass

        return Response({"success": True, "data": user_data})

    except Exception as e:
        traceback_str = traceback.format_exc()
        return Response({
            "success": False,
            "error": str(e),
            "trace": traceback_str
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
# Le décorateur @firebase_authenticated ne doit PAS être actif pour cette vue.
# Cette vue est destinée à CRÉER le profil utilisateur dans la base de données Django,
# donc l'utilisateur n'existe pas encore dans Django à ce stade.
# L'authentification Firebase (validation du token) est gérée par Firebase lui-même,
# mais la recherche d'un profil Django existant doit être évitée ici.
# @firebase_authenticated
def create_user_profile(request):
    """
    Vue API pour créer un profil utilisateur complet (client ou coiffeuse).
    Elle utilise UserCreationSerializer pour valider les données et créer les objets associés.
    """
    try:
        # 🔍 DEBUG: Afficher les données reçues
        print("=== DEBUG CREATE USER PROFILE ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        print(f"request.data: {request.data}")
        
        # Vérifier si une photo est présente
        if 'photo_profil' in request.FILES:
            photo = request.FILES['photo_profil']
            print(f"📷 Photo reçue: {photo.name}, taille: {photo.size} bytes")
        else:
            print("⚠️ Aucune photo dans request.FILES")
            
        if 'photo_profil' in request.data:
            print(f"📷 Photo dans request.data: {type(request.data['photo_profil'])}")
        else:
            print("⚠️ Aucune photo dans request.data")
        
        print("=====================================")

        serializer = UserCreationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "status": "success",
                "message": "Profil créé avec succès!",
                "data": serializer.to_representation(user)
            }, status=status.HTTP_201_CREATED)

        else:
            print(f"🚫 Erreurs de validation: {serializer.errors}")
            return Response({
                "status": "error",
                "message": "Erreurs de validation",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Erreur inattendue dans create_user_profile: {str(e)}")
        print(f"Traceback complet:\n{traceback.format_exc()}")

        return Response({
            "status": "error",
            "message": f"Une erreur interne est survenue: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@firebase_authenticated
def delete_my_profile_firebase(request):
    """
    Point de terminaison API pour la suppression complète du profil de l'utilisateur authentifié.
    L'utilisateur doit être authentifié via Firebase et ne peut supprimer que son propre compte.
    Supprime aussi le compte Firebase associé.
    """
    try:
        # 1. Récupérer l'utilisateur authentifié depuis le token Firebase
        authenticated_user = request.user
        user_uuid = authenticated_user.uuid

        logger.info(f"Tentative de suppression du profil pour UUID: {user_uuid}")

        # 2. Trouver l'utilisateur dans TblUser par son UUID
        try:
            target_user = TblUser.objects.get(uuid=user_uuid)
            user_id = target_user.idTblUser
        except TblUser.DoesNotExist:
            logger.error(f"Utilisateur avec UUID {user_uuid} non trouvé dans TblUser")
            return Response({
                "success": False,
                "message": "Profil utilisateur non trouvé dans la base de données.",
                "timestamp": timezone.now()
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. Récupérer l'UID Firebase pour la suppression du compte Firebase
        firebase_uid = None
        try:
            # Si vous stockez l'UID Firebase dans votre modèle, utilisez-le
            # Sinon, on essaiera de le récupérer par email
            if hasattr(authenticated_user, 'firebase_uid'):
                firebase_uid = authenticated_user.firebase_uid
            else:
                # Rechercher l'utilisateur Firebase par email
                firebase_user = auth.get_user_by_email(target_user.email)
                firebase_uid = firebase_user.uid

        except Exception as e:
            logger.warning(f"Impossible de récupérer l'UID Firebase: {str(e)}")
            # On continue sans supprimer le compte Firebase

        # 4. Initialiser le serializer pour la suppression
        serializer = DeleteProfileUserSerializer(
            data=request.data,
            context={
                'user': authenticated_user,
                'id_cible': user_id
            }
        )

        # 5. Validation et suppression des données Django
        if serializer.is_valid():
            try:
                # Supprimer les données dans Django
                deletion_summary = serializer.save()

                # 6. Supprimer le compte Firebase
                firebase_deletion_status = False
                if firebase_uid:
                    try:
                        auth.delete_user(firebase_uid)
                        firebase_deletion_status = True
                        logger.info(f"Compte Firebase {firebase_uid} supprimé avec succès")
                    except Exception as firebase_error:
                        logger.error(f"Erreur lors de la suppression Firebase: {str(firebase_error)}")
                        # On continue même si la suppression Firebase échoue

                # 7. Préparer la réponse
                response_data = {
                    "success": True,
                    "message": "Votre profil a été supprimé avec succès.",
                    "deletion_summary": deletion_summary,
                    "firebase_account_deleted": firebase_deletion_status,
                    "timestamp": timezone.now()
                }

                if not firebase_deletion_status and firebase_uid:
                    response_data[
                        "warning"] = "Le compte Firebase n'a pas pu être supprimé automatiquement. Contactez le support si nécessaire."

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Erreur lors de la suppression Django: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Erreur lors de la suppression du profil: {str(e)}",
                    "timestamp": timezone.now()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Validation échouée: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Validation échouée.",
                "errors": serializer.errors,
                "timestamp": timezone.now()
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur inattendue dans delete_my_profile_firebase: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne du serveur: {str(e)}",
            "timestamp": timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Configuration du logger pour débugger
logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
# @firebase_authenticated  # Décommentez si nécessaire
def delete_user_profile(request, idTblUser):
    """
    Point de terminaison API pour la suppression complète du profil d'un utilisateur
    spécifié par son ID.
    """
    try:
        # 1. Vérification préliminaire de l'ID
        logger.info(f"Tentative de suppression de l'utilisateur ID: {idTblUser}")

        # Convertir l'ID en entier pour éviter les erreurs de type
        try:
            user_id = int(idTblUser)
        except (ValueError, TypeError):
            return Response({
                "success": False,
                "message": "ID utilisateur invalide.",
                "deletion_summary": None,
                "timestamp": timezone.now()
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Vérifier que l'utilisateur cible existe
        try:
            target_user = TblUser.objects.get(idTblUser=user_id)  # Utiliser idTblUser au lieu de id
        except TblUser.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Utilisateur avec l'ID {user_id} non trouvé.",
                "deletion_summary": None,
                "timestamp": timezone.now()
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. Gestion de l'authentification
        # Si vous n'utilisez pas Firebase pour le moment, créez un utilisateur factice
        if not hasattr(request, 'user') or request.user is None:
            # Pour les tests, créez un utilisateur factice ou récupérez le premier admin
            try:
                # Option 1: Utiliser l'utilisateur cible lui-même (pour les tests)
                authenticated_user = target_user

                # Option 2: Ou utiliser un admin (décommentez si besoin)
                # authenticated_user = TblUser.objects.filter(role__nom='admin').first()
                # if not authenticated_user:
                #     authenticated_user = target_user

            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'utilisateur authentifié: {str(e)}")
                return Response({
                    "success": False,
                    "message": "Erreur d'authentification.",
                    "deletion_summary": None,
                    "timestamp": timezone.now()
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            authenticated_user = request.user

        # 4. Initialiser le serializer avec les bonnes données
        serializer = DeleteProfileUserSerializer(
            data=request.data,
            context={
                'user': authenticated_user,
                'id_cible': user_id  # Passer l'ID entier
            }
        )

        # 5. Validation et exécution
        if serializer.is_valid():
            try:
                deletion_summary = serializer.save()
                response_data = {
                    "success": True,
                    "message": "Profil et données associées supprimés avec succès.",
                    "deletion_summary": deletion_summary,
                    "timestamp": timezone.now()
                }

                # Vérifier si le serializer de réponse existe
                try:
                    response_serializer = DeleteProfileResponseSerializer(data=response_data)
                    response_serializer.is_valid(raise_exception=True)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                except Exception:
                    # Si le serializer de réponse n'existe pas, retourner directement les données
                    return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Erreur lors de la suppression : {str(e)}")
                response_data = {
                    "success": False,
                    "message": f"Erreur lors de la suppression : {str(e)}",
                    "deletion_summary": None,
                    "timestamp": timezone.now()
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Validation échouée : {serializer.errors}")
            response_data = {
                "success": False,
                "message": "Validation échouée.",
                "deletion_summary": serializer.errors,
                "timestamp": timezone.now()
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Catch-all pour toute erreur non prévue
        logger.error(f"Erreur inattendue dans delete_user_profile : {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne du serveur : {str(e)}",
            "deletion_summary": None,
            "timestamp": timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@firebase_authenticated  # Vérifie que l'utilisateur est authentifié
@is_owner(param_name="uuid", use_uuid=True)  # Vérifie que l'utilisateur est le propriétaire du compte
def update_user_phone(request, uuid):
    """
    Vue dédiée à la mise à jour du numéro de téléphone uniquement.

    Sécurité:
    - Nécessite une authentification Firebase
    - Vérifie que l'utilisateur connecté est le propriétaire du compte (uuid)

    Paramètres:
    - request: La requête HTTP
    - uuid: L'identifiant unique de l'utilisateur

    Corps de la requête attendu:
    {
        "numeroTelephone": "nouveau_numero"
    }

    Retourne:
    - 200 OK avec les données mises à jour si succès
    - 400 BAD REQUEST si requête invalide
    - 401 UNAUTHORIZED si non authentifié (via décorateur)
    - 403 FORBIDDEN si non propriétaire (via décorateur)
    - 404 NOT FOUND si utilisateur non trouvé
    - 500 INTERNAL SERVER ERROR pour les autres erreurs
    """
    # Cette vue ne nécessite pas de modification car elle ne traite que le numéro de téléphone
    # qui n'a pas changé dans le modèle

    # Vérifier que le corps de la requête contient uniquement le numéro de téléphone
    if 'numeroTelephone' not in request.data:
        return Response(
            {"error": "Le numéro de téléphone est requis"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Vérifier qu'il n'y a pas d'autres champs pour s'assurer que la vue est utilisée correctement
    if len(request.data.keys()) > 1:
        return Response(
            {"error": "Cette vue est réservée à la mise à jour du numéro de téléphone uniquement"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Récupérer l'utilisateur par UUID
        user = get_object_or_404(TblUser, uuid=uuid)

        # Récupérer le nouveau numéro
        new_phone = request.data['numeroTelephone']

        # Vérifier que le numéro est valide (vous pouvez ajouter des validations supplémentaires ici)
        if not new_phone or len(new_phone) < 3:  # Exemple de validation simple
            return Response(
                {"error": "Numéro de téléphone invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mettre à jour avec transaction pour assurer l'atomicité
        with transaction.atomic():
            # Sauvegarder l'ancien numéro pour le log
            old_phone = user.numero_telephone

            # Mettre à jour le numéro
            user.numero_telephone = new_phone
            user.save(update_fields=['numero_telephone'])

            # Log pour débogage
            print(f"Numéro de téléphone mis à jour pour l'utilisateur {uuid}")
            print(f"Ancien numéro: {old_phone} -> Nouveau numéro: {new_phone}")

        # Retourner une réponse de succès
        return Response({
            "success": True,
            "message": "Numéro de téléphone mis à jour avec succès",
            "data": {
                "uuid": uuid,
                "numeroTelephone": new_phone
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Gérer toutes les autres erreurs
        return Response(
            {"error": f"Erreur lors de la mise à jour: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
#@firebase_authenticated
#@is_owner(param_name="uuid", use_uuid=True)
def update_user_address(request, uuid):
    """
    🔄 Met à jour l'adresse d'un utilisateur avec le modèle existant.

    ✅ Compatible avec votre modèle TblAdresse actuel :
    - numero (CharField)
    - rue (ForeignKey vers TblRue)

    📌 Format JSON attendu en entrée :
    {
        "numero": "123",
        "rue": {
            "nomRue": "Rue des Fleurs",
            "localite": {
                "commune": "Bruxelles",
                "codePostal": "1000"
            }
        },
        // Ces champs sont acceptés mais ignorés (pour compatibilité frontend)
        "latitude": 50.8476,
        "longitude": 4.3572,
        "is_validated": true,
        "validation_date": "2025-06-09T10:30:00Z"
    }
    """

    try:
        # 🔍 Recherche de l'utilisateur via son UUID
        user = TblUser.objects.get(uuid=uuid)

        # 📥 Récupération des données de la requête
        address_data = request.data

        # 🚫 Validation de base des données
        if not address_data:
            return Response({
                "success": False,
                "message": "Aucune donnée d'adresse fournie"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🛡️ Validation des champs requis
        required_fields = ['numero', 'rue']
        missing_fields = [field for field in required_fields if field not in address_data]
        if missing_fields:
            return Response({
                "success": False,
                "message": f"Champs manquants: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🛡 Démarre une transaction pour garantir la cohérence
        with transaction.atomic():
            # 🔁 Si l'utilisateur a déjà une adresse, on l'utilise, sinon on crée une nouvelle instance
            address = user.adresse if user.adresse else TblAdresse()

            # 🏠 Mise à jour du numéro (validation du type et de la longueur)
            if 'numero' in address_data:
                numero = str(address_data['numero']).strip() if address_data['numero'] else ""

                if not numero:
                    return Response({
                        "success": False,
                        "message": "Le numéro ne peut pas être vide"
                    }, status=status.HTTP_400_BAD_REQUEST)

                if len(numero) > 5:  # Limite du modèle
                    return Response({
                        "success": False,
                        "message": "Le numéro ne peut pas dépasser 5 caractères"
                    }, status=status.HTTP_400_BAD_REQUEST)

                address.numero = numero

            # 📦 Traitement de la rue si présente
            if 'rue' in address_data:
                rue_data = address_data['rue']
                rue = address.rue if hasattr(address, 'rue') and address.rue else TblRue()

                # 🛣 Mise à jour du nom de la rue
                if 'nomRue' in rue_data:
                    nom_rue = rue_data['nomRue'].strip() if rue_data['nomRue'] else ""

                    if not nom_rue:
                        return Response({
                            "success": False,
                            "message": "Le nom de la rue ne peut pas être vide"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if len(nom_rue) > 50:  # Limite du modèle
                        return Response({
                            "success": False,
                            "message": "Le nom de la rue ne peut pas dépasser 50 caractères"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    rue.nom_rue = nom_rue

                # 🌍 Traitement de la localité imbriquée dans la rue
                if 'localite' in rue_data:
                    localite_data = rue_data['localite']
                    localite = rue.localite if hasattr(rue, 'localite') and rue.localite else TblLocalite()

                    # 🏘 Mise à jour des champs de localité avec validation
                    if 'commune' in localite_data:
                        commune = localite_data['commune'].strip() if localite_data['commune'] else ""

                        if not commune:
                            return Response({
                                "success": False,
                                "message": "La commune ne peut pas être vide"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        if len(commune) > 40:  # Limite du modèle
                            return Response({
                                "success": False,
                                "message": "La commune ne peut pas dépasser 40 caractères"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        localite.commune = commune

                    if 'codePostal' in localite_data:
                        code_postal = str(localite_data['codePostal']).strip() if localite_data['codePostal'] else ""

                        if not code_postal:
                            return Response({
                                "success": False,
                                "message": "Le code postal ne peut pas être vide"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        # Validation du format du code postal belge (4 chiffres)
                        if not code_postal.isdigit() or len(code_postal) != 4:
                            return Response({
                                "success": False,
                                "message": "Le code postal doit contenir exactement 4 chiffres"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        if len(code_postal) > 6:  # Limite du modèle
                            return Response({
                                "success": False,
                                "message": "Le code postal ne peut pas dépasser 6 caractères"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        localite.code_postal = code_postal

                    # 💾 Sauvegarde de la localité en base
                    localite.save()

                    # 🔗 Association de la localité à la rue
                    rue.localite = localite

                # 💾 Sauvegarde de la rue
                rue.save()

                # 🔗 Association de la rue à l'adresse
                address.rue = rue

            # 📍 Note : Les coordonnées GPS et données de validation sont ignorées
            # car elles ne font pas partie du modèle existant
            # Elles peuvent être stockées ailleurs ou simplement utilisées côté frontend

            # 💾 Sauvegarde de l'adresse complète
            address.save()

            # 🔗 Lier l'adresse à l'utilisateur
            user.adresse = address
            user.save()

            # 📊 Log de l'action (optionnel)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Adresse mise à jour pour l'utilisateur {user.uuid}")

            # 🧾 Sérialisation du résultat pour le retour JSON
            serializer = UserSerializer(user)

            # ✅ Réponse de succès avec les nouvelles données
            return Response({
                "success": True,
                "message": "Adresse mise à jour avec succès",
                "user": serializer.data
            }, status=status.HTTP_200_OK)

    # ❌ Gestion du cas où l'utilisateur n'existe pas
    except TblUser.DoesNotExist:
        return Response({
            "success": False,
            "message": "Utilisateur non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    # ⚠️ Gestion d'une erreur générale (ex: erreur de base de données)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors de la mise à jour de l'adresse pour {uuid}: {str(e)}")

        return Response({
            "success": False,
            "message": "Erreur interne du serveur"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
