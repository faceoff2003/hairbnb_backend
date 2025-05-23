import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from datetime import datetime
from hairbnb.services.geolocation_service import GeolocationService

from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import (
    TblUser, TblCoiffeuse, TblAdresse, TblRue, TblLocalite, TblCoiffeuseSalon, TblRole, TblSexe, TblType, TblClient
)
from hairbnb.profil.profil_serializers import UserSerializer, CoiffeuseSerializer, UserCreationSerializer


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


# Si vous avez un décorateur pour l'authentification Firebase, importez-le ici.
# Exemple : from your_app.decorators import firebase_authenticated


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
        serializer = UserCreationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "status": "success",
                "message": "Profil créé avec succès!",
                "data": serializer.to_representation(user)
            }, status=status.HTTP_201_CREATED)

        else:
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



# @csrf_exempt # Permet les requêtes POST sans jeton CSRF (utile pour les API, mais à gérer avec prudence en production)
# @api_view(['POST']) # Indique que cette fonction est une vue API qui accepte les requêtes POST
# # @firebase_authenticated # Décommentez cette ligne si vous utilisez un décorateur d'authentification Firebase
# def create_user_profile(request):
#     """
#     Vue API pour créer un profil utilisateur complet (client ou coiffeuse).
#     Elle utilise UserCreationSerializer pour valider les données et créer les objets associés.
#     """
#     try:
#         # Initialise le serializer avec les données reçues dans la requête.
#         # request.data gère automatiquement les données de formulaire, JSON, etc.
#         serializer = UserCreationSerializer(data=request.data)
#
#         # Valide les données selon les règles définies dans le serializer.
#         if serializer.is_valid():
#             # Si les données sont valides, appelle la méthode .save() du serializer.
#             # Cette méthode va exécuter la logique de création définie dans le serializer (méthode create()).
#             user = serializer.save()
#
#             # En cas de succès, renvoie une réponse HTTP 201 Created.
#             # Le champ 'data' contient la représentation de l'utilisateur créé,
#             # telle que définie par la méthode to_representation() du serializer.
#             return Response({
#                 "status": "success",
#                 "message": "Profil créé avec succès!",
#                 "data": serializer.to_representation(user)
#             }, status=status.HTTP_201_CREATED)
#
#         else:
#             # Si la validation échoue, les erreurs sont accessibles via serializer.errors.
#             # Ces erreurs sont formatées et renvoyées avec un statut 400 Bad Request.
#             return Response({
#                 "status": "error",
#                 "message": "Erreurs de validation",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         # Capture toute exception inattendue qui pourrait survenir pendant le processus.
#         # Affiche l'erreur et la trace complète dans la console du serveur pour le débogage.
#         print(f"Erreur inattendue dans create_user_profile: {str(e)}")
#         print(f"Traceback complet:\n{traceback.format_exc()}")
#
#         # Renvoie une réponse d'erreur générique avec un statut 500 Internal Server Error.
#         return Response({
#             "status": "error",
#             "message": f"Une erreur interne est survenue: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# @csrf_exempt
# @api_view(['POST'])
# # @firebase_authenticated  # Décommentez cette ligne si vous avez un décorateur d'authentification Firebase
# def create_user_profile(request):
#     """
#     Vue API pour créer un profil utilisateur complet (client ou coiffeuse).
#     Elle utilise UserCreationSerializer pour valider les données et créer les objets associés.
#     """
#     try:
#         # Le serializer est créé avec les données de la requête.
#         # request.data gère automatiquement les données de formulaire, JSON, etc.
#         serializer = UserCreationSerializer(data=request.data)
#
#         # La méthode is_valid() lance les validations définies dans le serializer.
#         if serializer.is_valid():
#             # La méthode .save() du serializer appelle la méthode create()
#             # que vous avez définie dans UserCreationSerializer.
#             user = serializer.save()
#
#             # Réponse de succès. Les données de l'utilisateur créé sont renvoyées via to_representation.
#             return Response({
#                 "status": "success",
#                 "message": "Profil créé avec succès!",
#                 "data": serializer.to_representation(user)
#             }, status=status.HTTP_201_CREATED)
#
#         else:
#             # Si la validation échoue, les erreurs sont accessibles via serializer.errors.
#             # Ces erreurs sont formatées et renvoyées avec un statut 400 Bad Request.
#             return Response({
#                 "status": "error",
#                 "message": "Erreurs de validation",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         # Gestion des erreurs imprévues.
#         # Il est bon de logger l'erreur et la trace complète pour le débogage.
#         print(f"Erreur inattendue dans create_user_profile: {str(e)}")
#         print(f"Traceback complet:\n{traceback.format_exc()}")
#
#         # Renvoie une réponse d'erreur générique avec un statut 500 Internal Server Error.
#         return Response({
#             "status": "error",
#             "message": f"Une erreur interne est survenue: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#



# @csrf_exempt
# @api_view(['POST'])
# #@firebase_authenticated
# def create_user_profile(request):
#     """
#     Vue POO pour créer un profil utilisateur complet.
#     Utilise un serializer pour validation et création.
#     """
#     try:
#         # Créer le serializer avec les données de la requête
#         serializer = UserCreationSerializer(data=request.data)
#
#         # Validation des données
#         if serializer.is_valid():
#             # Création de l'utilisateur via le serializer
#             user = serializer.save()
#
#             # Réponse de succès avec les données sérialisées
#             return Response({
#                 "status": "success",
#                 "message": "Profil créé avec succès!",
#                 "data": serializer.to_representation(user)
#             }, status=status.HTTP_201_CREATED)
#
#         else:
#             # Erreurs de validation
#             return Response({
#                 "status": "error",
#                 "message": "Erreurs de validation",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         # Gestion des erreurs non prévues
#         print(f"Erreur dans create_user_profile: {str(e)}")
#         print(f"Traceback: {traceback.format_exc()}")
#
#         return Response({
#             "status": "error",
#             "message": f"Erreur serveur: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @csrf_exempt
# @api_view(['POST'])
# @firebase_authenticated
# def create_user_profile(request):
#     """
#     Crée un profil utilisateur en fonction des données envoyées via une requête POST.
#     Nécessite une authentification Firebase.
#     """
#     try:
#         # Vérifiez si la requête contient des fichiers (multipart/form-data)
#         if request.content_type and request.content_type.startswith('multipart/form-data'):
#             # Utilisez request.POST et request.FILES
#             data = request.POST
#             photo_profil = request.FILES.get('photo_profil')
#         else:
#             # Sinon, lisez les données JSON dans request.body
#             data = json.loads(request.body)
#             photo_profil = None
#
#         # Debugging: Afficher les données reçues
#         print("Données reçues :", data)
#         print("Fichiers reçus :", request.FILES if hasattr(request, 'FILES') else 'Aucun')
#
#         # Champs obligatoires pour tous les utilisateurs
#         required_fields = [
#             'userUuid', 'email', 'role', 'nom', 'prenom', 'sexe',
#             'telephone', 'code_postal', 'commune', 'rue', 'numero', 'date_naissance'
#         ]
#         for field in required_fields:
#             if not data.get(field):
#                 return Response(
#                     {"status": "error", "message": f"Le champ {field} est obligatoire."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#         # Validation spécifique pour la date de naissance
#         try:
#             date_naissance = datetime.strptime(data['date_naissance'], '%d-%m-%Y').date()
#         except ValueError:
#             return Response(
#                 {"status": "error", "message": "Le format de la date de naissance doit être DD-MM-YYYY."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Vérifier si l'utilisateur existe déjà
#         user_uuid = data['userUuid']
#         if TblUser.objects.filter(uuid=user_uuid).exists():
#             return Response(
#                 {"status": "error", "message": "Utilisateur déjà existant"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # ✅ Récupérer ou créer les objets de référence
#         try:
#             role_obj = TblRole.objects.get(nom=data['role'])
#         except TblRole.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": f"Rôle '{data['role']}' non trouvé"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             sexe_obj = TblSexe.objects.get(libelle=data['sexe'])
#         except TblSexe.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": f"Sexe '{data['sexe']}' non trouvé"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             type_obj = TblType.objects.get(libelle=data['role'])  # role correspond au type
#         except TblType.DoesNotExist:
#             return Response(
#                 {"status": "error", "message": f"Type '{data['role']}' non trouvé"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Étape 2 : Gérer l'adresse
#         localite, _ = TblLocalite.objects.get_or_create(
#             commune=data['commune'],
#             code_postal=data['code_postal']
#         )
#         rue_obj, _ = TblRue.objects.get_or_create(
#             nom_rue=data['rue'],
#             localite=localite
#         )
#         adresse = TblAdresse.objects.create(
#             numero=data['numero'],
#             rue=rue_obj
#         )
#
#         # Étape 3 : Calculer les coordonnées géographiques avec le service
#         adresse_complete = f"{data['numero']}, {data['rue']}, {data['commune']}, {data['code_postal']}"
#         try:
#             latitude, longitude = GeolocationService.geocode_address(adresse_complete)
#         except Exception as e:
#             print(f"Erreur géolocalisation: {e}")
#             latitude, longitude = None, None
#
#         # Étape 4 : Créer un utilisateur de base
#         user = TblUser.objects.create(
#             uuid=user_uuid,
#             nom=data['nom'],
#             prenom=data['prenom'],
#             email=data['email'],
#             numero_telephone=data['telephone'],
#             adresse=adresse,
#             date_naissance=date_naissance,
#             photo_profil=photo_profil,
#             role=role_obj,
#             sexe_ref=sexe_obj,
#             type_ref=type_obj
#         )
#
#         # Étape 5 : Gérer les rôles spécifiques
#         if data['role'].lower() == 'coiffeuse':
#             coiffeuse = TblCoiffeuse.objects.create(
#                 idTblUser=user,
#                 nom_commercial=data.get('denomination_sociale'),  # Compatibilité ancien nom
#             )
#
#             # ✅ Si des coordonnées sont disponibles, on peut les stocker quelque part
#             # Pour l'instant, pas de champ position direct dans TblCoiffeuse
#             print(f"Coiffeuse créée: {coiffeuse.nom_commercial}")
#
#         elif data['role'].lower() == 'client':
#             client = TblClient.objects.create(idTblUser=user)
#             print(f"Client créé: {client.idTblUser.nom}")
#
#         # ✅ Réponse de succès avec informations de base
#         return Response({
#             "status": "success",
#             "message": "Profil créé avec succès!",
#             "data": {
#                 "user_id": user.idTblUser,
#                 "uuid": user.uuid,
#                 "nom": user.nom,
#                 "prenom": user.prenom,
#                 "email": user.email,
#                 "type": user.get_type(),
#                 "role": user.get_role()
#             }
#         }, status=status.HTTP_201_CREATED)
#
#     except json.JSONDecodeError:
#         return Response(
#             {"status": "error", "message": "Format JSON invalide"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     except Exception as e:
#         # Gestion des erreurs générales avec plus de détails
#         print(f"Erreur dans create_user_profile : {str(e)}")
#         import traceback
#         print(f"Traceback: {traceback.format_exc()}")
#
#         return Response(
#             {"status": "error", "message": f"Erreur serveur: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


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
@firebase_authenticated
@is_owner(param_name="uuid", use_uuid=True)
def update_user_address(request, uuid):
    """
    🔄 Met à jour l'adresse d'un utilisateur (partiellement ou totalement).

    ✅ Ce endpoint permet :
    - de modifier le numéro
    - de créer ou modifier la rue
    - de créer ou modifier la localité associée à cette rue

    ⚠️ Tous les objets imbriqués sont traités indépendamment :
    - Localité
    - Rue
    - Adresse

    📌 Format JSON attendu en entrée :
    {
        "numero": "123",
        "rue": {
            "nomRue": "Rue des Fleurs",
            "localite": {
                "commune": "Bruxelles",
                "codePostal": "1000"
            }
        }
    }
    """

    try:
        # 🔍 Recherche de l'utilisateur via son UUID
        user = TblUser.objects.get(uuid=uuid)

        # 📥 Récupération des données de la requête
        address_data = request.data

        # 🚫 Aucune donnée transmise
        if not address_data:
            return Response({"detail": "Aucune donnée d'adresse fournie"}, status=status.HTTP_400_BAD_REQUEST)

        # 🛡 Démarre une transaction pour garantir la cohérence des enregistrements liés
        with transaction.atomic():
            # 🔁 Si l'utilisateur a déjà une adresse, on l'utilise, sinon on crée une nouvelle instance
            address = user.adresse if user.adresse else TblAdresse()

            # 🏠 Mise à jour du numéro s'il est présent
            if 'numero' in address_data:
                address.numero = address_data['numero']

            # 📦 Traitement de la rue si présente
            if 'rue' in address_data:
                rue_data = address_data['rue']
                rue = address.rue if hasattr(address, 'rue') and address.rue else TblRue()

                # 🛣 Mise à jour du nom de la rue
                if 'nomRue' in rue_data:
                    rue.nom_rue = rue_data['nomRue']

                # 🌍 Traitement de la localité imbriquée dans la rue
                if 'localite' in rue_data:
                    localite_data = rue_data['localite']
                    localite = rue.localite if hasattr(rue, 'localite') and rue.localite else TblLocalite()

                    # 🏘 Mise à jour des champs de localité
                    if 'commune' in localite_data:
                        localite.commune = localite_data['commune']
                    if 'codePostal' in localite_data:
                        localite.code_postal = localite_data['codePostal']

                    # 💾 Sauvegarde de la localité en base
                    localite.save()

                    # 🔗 Association de la localité à la rue
                    rue.localite = localite

                # 💾 Sauvegarde de la rue
                rue.save()

                # 🔗 Association de la rue à l'adresse
                address.rue = rue

            # 💾 Sauvegarde de l'adresse complète
            address.save()

            # 🔗 Lier l'adresse à l'utilisateur
            user.adresse = address
            user.save()

            # 🧾 Sérialisation du résultat pour le retour JSON
            serializer = UserSerializer(user)

            # ✅ Réponse de succès avec les nouvelles données
            return Response({
                "message": "Adresse mise à jour avec succès",
                "user": serializer.data
            }, status=status.HTTP_200_OK)

    # ❌ Gestion du cas où l'utilisateur n'existe pas
    except TblUser.DoesNotExist:
        return Response({"detail": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    # ⚠️ Gestion d'une erreur générale (ex: erreur de base de données)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








# import traceback
#
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
# from decorators.decorators import firebase_authenticated, is_owner
# from hairbnb.models import (
#     TblUser, TblCoiffeuse, TblAdresse, TblRue, TblLocalite
# )
# from hairbnb.profil.profil_serializers import UserSerializer, CoiffeuseSerializer
#
#
# @csrf_exempt
# @api_view(['GET'])
# def get_user_profile(request, userUuid):
#     try:
#         # Récupérer l'utilisateur
#         user = get_object_or_404(TblUser, uuid=userUuid)
#
#         # Utiliser le serializer approprié
#         user_serializer = UserSerializer(user)
#         user_data = user_serializer.data
#
#         # Ajouter l'adresse formatée pour plus de facilité d'utilisation côté client
#         if user.adresse:
#             user_data.update({
#                 "adresse_formatee": f"{user.adresse.numero}, {user.adresse.rue.nom_rue}",
#                 "code_postal": user.adresse.rue.localite.code_postal,
#                 "commune": user.adresse.rue.localite.commune,
#             })
#
#         # Vérifier si l'utilisateur est une coiffeuse et ajouter les informations professionnelles
#         try:
#             if hasattr(user, 'type_ref') and user.type_ref and user.type_ref.libelle == "coiffeuse" and hasattr(user,
#                                                                                                                 'coiffeuse'):
#                 coiffeuse_serializer = CoiffeuseSerializer(user.coiffeuse)
#                 # On ne garde que les informations professionnelles spécifiques
#                 pro_data = {
#                     "nom_commercial": coiffeuse_serializer.data['nom_commercial'],
#                 }
#
#                 # Ajouter le numéro de TVA s'il existe
#                 if user.coiffeuse.numero_tva:
#                     tva_serializer = NumeroTVASerializer(user.coiffeuse.numero_tva)
#                     pro_data["numero_tva"] = tva_serializer.data['numero_tva']
#
#                 user_data.update({
#                     "coiffeuse_data": pro_data
#                 })
#
#                 # Ajouter les informations du salon si la coiffeuse a un salon
#                 if hasattr(user.coiffeuse, 'salon_direct'):
#                     salon = user.coiffeuse.salon_direct
#                     salon_data = {
#                         "idTblSalon": salon.idTblSalon,
#                         "nom_salon": salon.nom_salon,
#                         "position": salon.position
#                     }
#                     user_data["salon_data"] = salon_data
#         except TblCoiffeuse.DoesNotExist:
#             # Si l'utilisateur n'a pas d'entrée dans la table coiffeuse, on ne fait rien
#             pass
#
#         return Response({"success": True, "data": user_data})
#
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         return Response({
#             "success": False,
#             "error": str(e),
#             "trace": traceback_str
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['PATCH'])
# @firebase_authenticated  # Vérifie que l'utilisateur est authentifié
# @is_owner(param_name="uuid", use_uuid=True)  # Vérifie que l'utilisateur est le propriétaire du compte
# def update_user_phone(request, uuid):
#     """
#     Vue dédiée à la mise à jour du numéro de téléphone uniquement.
#
#     Sécurité:
#     - Nécessite une authentification Firebase
#     - Vérifie que l'utilisateur connecté est le propriétaire du compte (uuid)
#
#     Paramètres:
#     - request: La requête HTTP
#     - uuid: L'identifiant unique de l'utilisateur
#
#     Corps de la requête attendu:
#     {
#         "numeroTelephone": "nouveau_numero"
#     }
#
#     Retourne:
#     - 200 OK avec les données mises à jour si succès
#     - 400 BAD REQUEST si requête invalide
#     - 401 UNAUTHORIZED si non authentifié (via décorateur)
#     - 403 FORBIDDEN si non propriétaire (via décorateur)
#     - 404 NOT FOUND si utilisateur non trouvé
#     - 500 INTERNAL SERVER ERROR pour les autres erreurs
#     """
#     # Cette vue ne nécessite pas de modification car elle ne traite que le numéro de téléphone
#     # qui n'a pas changé dans le modèle
#
#     # Vérifier que le corps de la requête contient uniquement le numéro de téléphone
#     if 'numeroTelephone' not in request.data:
#         return Response(
#             {"error": "Le numéro de téléphone est requis"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # Vérifier qu'il n'y a pas d'autres champs pour s'assurer que la vue est utilisée correctement
#     if len(request.data.keys()) > 1:
#         return Response(
#             {"error": "Cette vue est réservée à la mise à jour du numéro de téléphone uniquement"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     try:
#         # Récupérer l'utilisateur par UUID
#         user = get_object_or_404(TblUser, uuid=uuid)
#
#         # Récupérer le nouveau numéro
#         new_phone = request.data['numeroTelephone']
#
#         # Vérifier que le numéro est valide (vous pouvez ajouter des validations supplémentaires ici)
#         if not new_phone or len(new_phone) < 3:  # Exemple de validation simple
#             return Response(
#                 {"error": "Numéro de téléphone invalide"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Mettre à jour avec transaction pour assurer l'atomicité
#         with transaction.atomic():
#             # Sauvegarder l'ancien numéro pour le log
#             old_phone = user.numero_telephone
#
#             # Mettre à jour le numéro
#             user.numero_telephone = new_phone
#             user.save(update_fields=['numero_telephone'])
#
#             # Log pour débogage
#             print(f"Numéro de téléphone mis à jour pour l'utilisateur {uuid}")
#             print(f"Ancien numéro: {old_phone} -> Nouveau numéro: {new_phone}")
#
#         # Retourner une réponse de succès
#         return Response({
#             "success": True,
#             "message": "Numéro de téléphone mis à jour avec succès",
#             "data": {
#                 "uuid": uuid,
#                 "numeroTelephone": new_phone
#             }
#         }, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         # Gérer toutes les autres erreurs
#         return Response(
#             {"error": f"Erreur lors de la mise à jour: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#
#
# @api_view(['PATCH'])
# @firebase_authenticated
# @is_owner(param_name="uuid", use_uuid=True)
# def update_user_address(request, uuid):
#     """
#     🔄 Met à jour l'adresse d'un utilisateur (partiellement ou totalement).
#
#     ✅ Ce endpoint permet :
#     - de modifier le numéro (y compris la boîte postale intégrée)
#     - de créer ou modifier la rue
#     - de créer ou modifier la localité associée à cette rue
#
#     ⚠️ Tous les objets imbriqués sont traités indépendamment :
#     - Localité
#     - Rue
#     - Adresse
#
#     📌 Format JSON attendu en entrée :
#     {
#         "numero": "123",
#         "boitePostale": "A",  // Optionnel: sera combiné avec numéro
#         "rue": {
#             "nomRue": "Rue des Fleurs",
#             "localite": {
#                 "commune": "Bruxelles",
#                 "codePostal": "1000"
#             }
#         }
#     }
#     """
#
#     try:
#         # 🔍 Recherche de l'utilisateur via son UUID
#         user = TblUser.objects.get(uuid=uuid)
#
#         # 📥 Récupération des données de la requête
#         address_data = request.data
#
#         # 🚫 Aucune donnée transmise
#         if not address_data:
#             return Response({"detail": "Aucune donnée d'adresse fournie"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # 🛡 Démarre une transaction pour garantir la cohérence des enregistrements liés
#         with transaction.atomic():
#             # 🔁 Si l'utilisateur a déjà une adresse, on l'utilise, sinon on crée une nouvelle instance
#             address = user.adresse if user.adresse else TblAdresse()
#
#             # 🏠 Mise à jour du numéro s'il est présent
#             if 'numero' in address_data:
#                 numero = address_data['numero']
#
#                 # Vérifier si une boîte postale est fournie séparément
#                 if 'boitePostale' in address_data and address_data['boitePostale']:
#                     # Combiner le numéro et la boîte postale
#                     numero = f"{numero}/{address_data['boitePostale']}"
#
#                 address.numero = numero
#
#             # 📦 Traitement de la rue si présente
#             if 'rue' in address_data:
#                 rue_data = address_data['rue']
#                 rue = address.rue if hasattr(address, 'rue') and address.rue else TblRue()
#
#                 # 🛣 Mise à jour du nom de la rue
#                 if 'nomRue' in rue_data:
#                     rue.nom_rue = rue_data['nomRue']
#
#                 # 🌍 Traitement de la localité imbriquée dans la rue
#                 if 'localite' in rue_data:
#                     localite_data = rue_data['localite']
#                     localite = rue.localite if hasattr(rue, 'localite') and rue.localite else TblLocalite()
#
#                     # 🏘 Mise à jour des champs de localité
#                     if 'commune' in localite_data:
#                         localite.commune = localite_data['commune']
#                     if 'codePostal' in localite_data:
#                         localite.code_postal = localite_data['codePostal']
#
#                     # 💾 Sauvegarde de la localité en base
#                     localite.save()
#
#                     # 🔗 Association de la localité à la rue
#                     rue.localite = localite
#
#                 # 💾 Sauvegarde de la rue
#                 rue.save()
#
#                 # 🔗 Association de la rue à l'adresse
#                 address.rue = rue
#
#             # 💾 Sauvegarde de l'adresse complète
#             address.save()
#
#             # 🔗 Lier l'adresse à l'utilisateur
#             user.adresse = address
#             user.save()
#
#             # 🧾 Sérialisation du résultat pour le retour JSON
#             serializer = UserSerializer(user)
#
#             # ✅ Réponse de succès avec les nouvelles données
#             return Response({
#                 "message": "Adresse mise à jour avec succès",
#                 "user": serializer.data
#             }, status=status.HTTP_200_OK)
#
#     # ❌ Gestion du cas où l'utilisateur n'existe pas
#     except TblUser.DoesNotExist:
#         return Response({"detail": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
#
#     # ⚠️ Gestion d'une erreur générale (ex: erreur de base de données)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # import traceback
# #
# # from django.db import transaction
# # from django.shortcuts import get_object_or_404
# # from django.views.decorators.csrf import csrf_exempt
# # from rest_framework import status
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# #
# # from decorators.decorators import firebase_authenticated, is_owner
# # from hairbnb.models import (
# #     TblUser, TblCoiffeuse, TblAdresse, TblRue, TblLocalite, TblNumeroTVA
# # )
# # from hairbnb.profil.profil_serializers import UserSerializer, CoiffeuseSerializer, NumeroTVASerializer
# #
# #
# # @csrf_exempt
# # @api_view(['GET'])
# # def get_user_profile(request, userUuid):
# #     try:
# #         # Récupérer l'utilisateur
# #         user = get_object_or_404(TblUser, uuid=userUuid)
# #
# #         # Utiliser le serializer approprié
# #         user_serializer = UserSerializer(user)
# #         user_data = user_serializer.data
# #
# #         # Ajouter l'adresse formatée pour plus de facilité d'utilisation côté client
# #         if user.adresse:
# #             user_data.update({
# #                 "adresse_formatee": f"{user.adresse.numero}, {user.adresse.rue.nom_rue}",
# #                 "code_postal": user.adresse.rue.localite.code_postal,
# #                 "commune": user.adresse.rue.localite.commune,
# #             })
# #
# #             # Ajouter les boîtes postales si elles existent
# #             boites_postales = user.adresse.boites_postales.all()
# #             if boites_postales.exists():
# #                 bp_list = [bp.numero_bp for bp in boites_postales]
# #                 user_data["boites_postales"] = bp_list
# #
# #         # Vérifier si l'utilisateur est une coiffeuse et ajouter les informations professionnelles
# #         try:
# #             if hasattr(user, 'type_ref') and user.type_ref and user.type_ref.libelle == "coiffeuse" and hasattr(user,
# #                                                                                                                 'coiffeuse'):
# #                 coiffeuse_serializer = CoiffeuseSerializer(user.coiffeuse)
# #                 # On ne garde que les informations professionnelles spécifiques
# #                 pro_data = {
# #                     "nom_commercial": coiffeuse_serializer.data['nom_commercial'],
# #                 }
# #
# #                 # Ajouter le numéro de TVA s'il existe
# #                 if user.coiffeuse.numero_tva:
# #                     tva_serializer = NumeroTVASerializer(user.coiffeuse.numero_tva)
# #                     pro_data["numero_tva"] = tva_serializer.data['numero_tva']
# #
# #                 user_data.update({
# #                     "coiffeuse_data": pro_data
# #                 })
# #
# #                 # Ajouter les informations du salon si la coiffeuse a un salon
# #                 if hasattr(user.coiffeuse, 'salon_direct'):
# #                     salon = user.coiffeuse.salon_direct
# #                     salon_data = {
# #                         "idTblSalon": salon.idTblSalon,
# #                         "nom_salon": salon.nom_salon,
# #                         "position": salon.position
# #                     }
# #                     user_data["salon_data"] = salon_data
# #         except TblCoiffeuse.DoesNotExist:
# #             # Si l'utilisateur n'a pas d'entrée dans la table coiffeuse, on ne fait rien
# #             pass
# #
# #         return Response({"success": True, "data": user_data})
# #
# #     except Exception as e:
# #         traceback_str = traceback.format_exc()
# #         return Response({
# #             "success": False,
# #             "error": str(e),
# #             "trace": traceback_str
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #
# #
# # @api_view(['PATCH'])
# # @firebase_authenticated  # Vérifie que l'utilisateur est authentifié
# # @is_owner(param_name="uuid", use_uuid=True)  # Vérifie que l'utilisateur est le propriétaire du compte
# # def update_user_phone(request, uuid):
# #     """
# #     Vue dédiée à la mise à jour du numéro de téléphone uniquement.
# #
# #     Sécurité:
# #     - Nécessite une authentification Firebase
# #     - Vérifie que l'utilisateur connecté est le propriétaire du compte (uuid)
# #
# #     Paramètres:
# #     - request: La requête HTTP
# #     - uuid: L'identifiant unique de l'utilisateur
# #
# #     Corps de la requête attendu:
# #     {
# #         "numeroTelephone": "nouveau_numero"
# #     }
# #
# #     Retourne:
# #     - 200 OK avec les données mises à jour si succès
# #     - 400 BAD REQUEST si requête invalide
# #     - 401 UNAUTHORIZED si non authentifié (via décorateur)
# #     - 403 FORBIDDEN si non propriétaire (via décorateur)
# #     - 404 NOT FOUND si utilisateur non trouvé
# #     - 500 INTERNAL SERVER ERROR pour les autres erreurs
# #     """
# #     # Cette vue ne nécessite pas de modification car elle ne traite que le numéro de téléphone
# #     # qui n'a pas changé dans le modèle
# #
# #     # Vérifier que le corps de la requête contient uniquement le numéro de téléphone
# #     if 'numeroTelephone' not in request.data:
# #         return Response(
# #             {"error": "Le numéro de téléphone est requis"},
# #             status=status.HTTP_400_BAD_REQUEST
# #         )
# #
# #     # Vérifier qu'il n'y a pas d'autres champs pour s'assurer que la vue est utilisée correctement
# #     if len(request.data.keys()) > 1:
# #         return Response(
# #             {"error": "Cette vue est réservée à la mise à jour du numéro de téléphone uniquement"},
# #             status=status.HTTP_400_BAD_REQUEST
# #         )
# #
# #     try:
# #         # Récupérer l'utilisateur par UUID
# #         user = get_object_or_404(TblUser, uuid=uuid)
# #
# #         # Récupérer le nouveau numéro
# #         new_phone = request.data['numeroTelephone']
# #
# #         # Vérifier que le numéro est valide (vous pouvez ajouter des validations supplémentaires ici)
# #         if not new_phone or len(new_phone) < 3:  # Exemple de validation simple
# #             return Response(
# #                 {"error": "Numéro de téléphone invalide"},
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )
# #
# #         # Mettre à jour avec transaction pour assurer l'atomicité
# #         with transaction.atomic():
# #             # Sauvegarder l'ancien numéro pour le log
# #             old_phone = user.numero_telephone
# #
# #             # Mettre à jour le numéro
# #             user.numero_telephone = new_phone
# #             user.save(update_fields=['numero_telephone'])
# #
# #             # Log pour débogage
# #             print(f"Numéro de téléphone mis à jour pour l'utilisateur {uuid}")
# #             print(f"Ancien numéro: {old_phone} -> Nouveau numéro: {new_phone}")
# #
# #         # Retourner une réponse de succès
# #         return Response({
# #             "success": True,
# #             "message": "Numéro de téléphone mis à jour avec succès",
# #             "data": {
# #                 "uuid": uuid,
# #                 "numeroTelephone": new_phone
# #             }
# #         }, status=status.HTTP_200_OK)
# #
# #     except Exception as e:
# #         # Gérer toutes les autres erreurs
# #         return Response(
# #             {"error": f"Erreur lors de la mise à jour: {str(e)}"},
# #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
# #         )
# #
# #
# # @api_view(['PATCH'])
# # @firebase_authenticated
# # @is_owner(param_name="uuid", use_uuid=True)
# # def update_user_address(request, uuid):
# #     """
# #     🔄 Met à jour l'adresse d'un utilisateur (partiellement ou totalement).
# #
# #     ✅ Ce endpoint permet :
# #     - de modifier le numéro
# #     - de créer ou modifier les boîtes postales associées
# #     - de créer ou modifier la rue
# #     - de créer ou modifier la localité associée à cette rue
# #
# #     ⚠️ Tous les objets imbriqués sont traités indépendamment :
# #     - Localité
# #     - Rue
# #     - Adresse
# #     - Boîtes Postales
# #
# #     📌 Format JSON attendu en entrée :
# #     {
# #         "numero": "123",
# #         "boitesPostales": ["4A", "5B"],  // Optionnel: liste des numéros de boîtes postales
# #         "rue": {
# #             "nomRue": "Rue des Fleurs",
# #             "localite": {
# #                 "commune": "Bruxelles",
# #                 "codePostal": "1000"
# #             }
# #         }
# #     }
# #     """
# #
# #     try:
# #         # 🔍 Recherche de l'utilisateur via son UUID
# #         user = TblUser.objects.get(uuid=uuid)
# #
# #         # 📥 Récupération des données de la requête
# #         address_data = request.data
# #
# #         # 🚫 Aucune donnée transmise
# #         if not address_data:
# #             return Response({"detail": "Aucune donnée d'adresse fournie"}, status=status.HTTP_400_BAD_REQUEST)
# #
# #         # 🛡 Démarre une transaction pour garantir la cohérence des enregistrements liés
# #         with transaction.atomic():
# #             # 🔁 Si l'utilisateur a déjà une adresse, on l'utilise, sinon on crée une nouvelle instance
# #             address = user.adresse if user.adresse else TblAdresse()
# #
# #             # 🏠 Mise à jour du numéro s'il est présent
# #             if 'numero' in address_data:
# #                 address.numero = address_data['numero']
# #
# #             # 📦 Traitement de la rue si présente
# #             if 'rue' in address_data:
# #                 rue_data = address_data['rue']
# #                 rue = address.rue if hasattr(address, 'rue') and address.rue else TblRue()
# #
# #                 # 🛣 Mise à jour du nom de la rue
# #                 if 'nomRue' in rue_data:
# #                     rue.nom_rue = rue_data['nomRue']
# #
# #                 # 🌍 Traitement de la localité imbriquée dans la rue
# #                 if 'localite' in rue_data:
# #                     localite_data = rue_data['localite']
# #                     localite = rue.localite if hasattr(rue, 'localite') and rue.localite else TblLocalite()
# #
# #                     # 🏘 Mise à jour des champs de localité
# #                     if 'commune' in localite_data:
# #                         localite.commune = localite_data['commune']
# #                     if 'codePostal' in localite_data:
# #                         localite.code_postal = localite_data['codePostal']
# #
# #                     # 💾 Sauvegarde de la localité en base
# #                     localite.save()
# #
# #                     # 🔗 Association de la localité à la rue
# #                     rue.localite = localite
# #
# #                 # 💾 Sauvegarde de la rue
# #                 rue.save()
# #
# #                 # 🔗 Association de la rue à l'adresse
# #                 address.rue = rue
# #
# #             # 💾 Sauvegarde de l'adresse complète
# #             address.save()
# #
# #             # 🔗 Lier l'adresse à l'utilisateur
# #             user.adresse = address
# #             user.save()
# #
# #             # 📮 Traitement des boîtes postales si présentes
# #             if 'boitesPostales' in address_data and isinstance(address_data['boitesPostales'], list):
# #                 # Supprimer les anciennes boîtes postales
# #                 address.boites_postales.all().delete()
# #
# #                 # Créer les nouvelles boîtes postales
# #                 for numero_bp in address_data['boitesPostales']:
# #                     TblBoitePostale.objects.create(
# #                         adresse=address,
# #                         numero_bp=numero_bp
# #                     )
# #
# #             # 🧾 Sérialisation du résultat pour le retour JSON
# #             serializer = UserSerializer(user)
# #
# #             # ✅ Réponse de succès avec les nouvelles données
# #             return Response({
# #                 "message": "Adresse mise à jour avec succès",
# #                 "user": serializer.data
# #             }, status=status.HTTP_200_OK)
# #
# #     # ❌ Gestion du cas où l'utilisateur n'existe pas
# #     except TblUser.DoesNotExist:
# #         return Response({"detail": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
# #
# #     # ⚠️ Gestion d'une erreur générale (ex: erreur de base de données)
# #     except Exception as e:
# #         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
#
#
#
#
#
#
# # import traceback
# #
# # from django.db import transaction
# # from django.shortcuts import get_object_or_404
# # from django.views.decorators.csrf import csrf_exempt
# # from rest_framework import status
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# #
# # from decorators.decorators import firebase_authenticated, is_owner
# # from hairbnb.models import TblUser, TblCoiffeuse, TblAdresse, TblRue, TblLocalite
# # from hairbnb.profil.profil_serializers import UserSerializer, CoiffeuseSerializer
# #
# #
# # @csrf_exempt
# # @api_view(['GET'])
# # def get_user_profile(request, userUuid):
# #     try:
# #         # Récupérer l'utilisateur
# #         user = get_object_or_404(TblUser, uuid=userUuid)
# #
# #         # Utiliser le serializer approprié
# #         user_serializer = UserSerializer(user)
# #         user_data = user_serializer.data
# #
# #         # Ajouter l'adresse formatée pour plus de facilité d'utilisation côté client
# #         if user.adresse:
# #             user_data.update({
# #                 "adresse_formatee": f"{user.adresse.numero}, {user.adresse.rue.nom_rue}",
# #                 "code_postal": user.adresse.rue.localite.code_postal,
# #                 "commune": user.adresse.rue.localite.commune,
# #             })
# #
# #         # Vérifier si l'utilisateur est une coiffeuse et ajouter les informations professionnelles
# #         try:
# #             if hasattr(user, 'type_ref') and user.type_ref and user.type_ref.libelle == "coiffeuse" and hasattr(user,
# #                                                                                                                 'coiffeuse'):
# #                 coiffeuse_serializer = CoiffeuseSerializer(user.coiffeuse)
# #                 # On ne garde que les informations professionnelles spécifiques
# #                 pro_data = {
# #                     "denomination_sociale": coiffeuse_serializer.data['denomination_sociale'],
# #                     "tva": coiffeuse_serializer.data['tva'],
# #                     "position": coiffeuse_serializer.data['position'],
# #                 }
# #                 user_data.update({
# #                     "coiffeuse_data": pro_data
# #                 })
# #         except TblCoiffeuse.DoesNotExist:
# #             # Si l'utilisateur n'a pas d'entrée dans la table coiffeuse, on ne fait rien
# #             pass
# #
# #         return Response({"success": True, "data": user_data})
# #
# #
# #     except Exception as e:
# #
# #         traceback_str = traceback.format_exc()
# #
# #         return Response({
# #
# #             "success": False,
# #
# #             "error": str(e),
# #
# #             "trace": traceback_str
# #
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #
# #
# # @api_view(['PATCH'])
# # @firebase_authenticated  # Vérifie que l'utilisateur est authentifié
# # @is_owner(param_name="uuid", use_uuid=True)  # Vérifie que l'utilisateur est le propriétaire du compte
# # def update_user_phone(request, uuid):
# #     """
# #     Vue dédiée à la mise à jour du numéro de téléphone uniquement.
# #
# #     Sécurité:
# #     - Nécessite une authentification Firebase
# #     - Vérifie que l'utilisateur connecté est le propriétaire du compte (uuid)
# #
# #     Paramètres:
# #     - request: La requête HTTP
# #     - uuid: L'identifiant unique de l'utilisateur
# #
# #     Corps de la requête attendu:
# #     {
# #         "numeroTelephone": "nouveau_numero"
# #     }
# #
# #     Retourne:
# #     - 200 OK avec les données mises à jour si succès
# #     - 400 BAD REQUEST si requête invalide
# #     - 401 UNAUTHORIZED si non authentifié (via décorateur)
# #     - 403 FORBIDDEN si non propriétaire (via décorateur)
# #     - 404 NOT FOUND si utilisateur non trouvé
# #     - 500 INTERNAL SERVER ERROR pour les autres erreurs
# #     """
# #     # Vérifier que le corps de la requête contient uniquement le numéro de téléphone
# #     if 'numeroTelephone' not in request.data:
# #         return Response(
# #             {"error": "Le numéro de téléphone est requis"},
# #             status=status.HTTP_400_BAD_REQUEST
# #         )
# #
# #     # Vérifier qu'il n'y a pas d'autres champs pour s'assurer que la vue est utilisée correctement
# #     if len(request.data.keys()) > 1:
# #         return Response(
# #             {"error": "Cette vue est réservée à la mise à jour du numéro de téléphone uniquement"},
# #             status=status.HTTP_400_BAD_REQUEST
# #         )
# #
# #     try:
# #         # Récupérer l'utilisateur par UUID
# #         user = get_object_or_404(TblUser, uuid=uuid)
# #
# #         # Récupérer le nouveau numéro
# #         new_phone = request.data['numeroTelephone']
# #
# #         # Vérifier que le numéro est valide (vous pouvez ajouter des validations supplémentaires ici)
# #         if not new_phone or len(new_phone) < 3:  # Exemple de validation simple
# #             return Response(
# #                 {"error": "Numéro de téléphone invalide"},
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )
# #
# #         # Mettre à jour avec transaction pour assurer l'atomicité
# #         with transaction.atomic():
# #             # Sauvegarder l'ancien numéro pour le log
# #             old_phone = user.numero_telephone
# #
# #             # Mettre à jour le numéro
# #             user.numero_telephone = new_phone
# #             user.save(update_fields=['numero_telephone'])
# #
# #             # Log pour débogage
# #             print(f"Numéro de téléphone mis à jour pour l'utilisateur {uuid}")
# #             print(f"Ancien numéro: {old_phone} -> Nouveau numéro: {new_phone}")
# #
# #         # Retourner une réponse de succès
# #         return Response({
# #             "success": True,
# #             "message": "Numéro de téléphone mis à jour avec succès",
# #             "data": {
# #                 "uuid": uuid,
# #                 "numeroTelephone": new_phone
# #             }
# #         }, status=status.HTTP_200_OK)
# #
# #     except Exception as e:
# #         # Gérer toutes les autres erreurs
# #         return Response(
# #             {"error": f"Erreur lors de la mise à jour: {str(e)}"},
# #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
# #         )
# #
# #
# # # Import des décorateurs et outils nécessaires
# # @api_view(['PATCH'])  # Spécifie que cette vue accepte uniquement les requêtes HTTP PATCH
# # @firebase_authenticated  # Décorateur personnalisé pour vérifier l'authentification Firebase
# # @is_owner(param_name="uuid", use_uuid=True)
# #   # Vérifie que l'utilisateur connecté est bien propriétaire des données (UUID correspond)
# # def update_user_address(request, uuid):
# #     """
# #     🔄 Met à jour l'adresse d'un utilisateur (partiellement ou totalement).
# #
# #     ✅ Ce endpoint permet :
# #     - de modifier le numéro et la boîte postale
# #     - de créer ou modifier la rue
# #     - de créer ou modifier la localité associée à cette rue
# #
# #     ⚠️ Tous les objets imbriqués sont traités indépendamment :
# #     - Localité
# #     - Rue
# #     - Adresse
# #
# #     📌 Format JSON attendu en entrée :
# #     {
# #         "numero": "123",
# #         "boitePostale": "4A",
# #         "rue": {
# #             "nomRue": "Rue des Fleurs",
# #             "localite": {
# #                 "commune": "Bruxelles",
# #                 "codePostal": "1000"
# #             }
# #         }
# #     }
# #     """
# #
# #     try:
# #         # 🔍 Recherche de l'utilisateur via son UUID
# #         user = TblUser.objects.get(uuid=uuid)
# #
# #         # 📥 Récupération des données de la requête
# #         address_data = request.data
# #
# #         # 🚫 Aucune donnée transmise
# #         if not address_data:
# #             return Response({"detail": "Aucune donnée d'adresse fournie"}, status=status.HTTP_400_BAD_REQUEST)
# #
# #         # 🛡 Démarre une transaction pour garantir la cohérence des enregistrements liés
# #         with transaction.atomic():
# #             # 🔁 Si l'utilisateur a déjà une adresse, on l'utilise, sinon on crée une nouvelle instance
# #             address = user.adresse if user.adresse else TblAdresse()
# #
# #             # 🏠 Mise à jour du numéro et de la boîte postale s'ils sont présents
# #             if 'numero' in address_data:
# #                 address.numero = address_data['numero']
# #             if 'boitePostale' in address_data:
# #                 address.boite_postale = address_data['boitePostale']
# #
# #             # 📦 Traitement de la rue si présente
# #             if 'rue' in address_data:
# #                 rue_data = address_data['rue']
# #                 rue = address.rue if address.rue else TblRue()
# #
# #                 # 🛣 Mise à jour du nom de la rue
# #                 if 'nomRue' in rue_data:
# #                     rue.nom_rue = rue_data['nomRue']
# #
# #                 # 🌍 Traitement de la localité imbriquée dans la rue
# #                 if 'localite' in rue_data:
# #                     localite_data = rue_data['localite']
# #                     localite = rue.localite if rue.localite else TblLocalite()
# #
# #                     # 🏘 Mise à jour des champs de localité
# #                     if 'commune' in localite_data:
# #                         localite.commune = localite_data['commune']
# #                     if 'codePostal' in localite_data:
# #                         localite.code_postal = localite_data['codePostal']
# #
# #                     # 💾 Sauvegarde de la localité en base
# #                     localite.save()
# #
# #                     # 🔗 Association de la localité à la rue
# #                     rue.localite = localite
# #
# #                 # 💾 Sauvegarde de la rue
# #                 rue.save()
# #
# #                 # 🔗 Association de la rue à l'adresse
# #                 address.rue = rue
# #
# #             # 💾 Sauvegarde de l'adresse complète
# #             address.save()
# #
# #             # 🔗 Lier l'adresse à l'utilisateur
# #             user.adresse = address
# #             user.save()
# #
# #             # 🧾 Sérialisation du résultat pour le retour JSON
# #             serializer = UserSerializer(user)
# #
# #             # ✅ Réponse de succès avec les nouvelles données
# #             return Response({
# #                 "message": "Adresse mise à jour avec succès",
# #                 "user": serializer.data
# #             }, status=status.HTTP_200_OK)
# #
# #     # ❌ Gestion du cas où l'utilisateur n'existe pas
# #     except TblUser.DoesNotExist:
# #         return Response({"detail": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
# #
# #     # ⚠️ Gestion d'une erreur générale (ex: erreur de base de données)
# #     except Exception as e:
# #         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #
