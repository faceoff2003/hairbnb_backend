import logging
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TblAdresse, TblRue, TblLocalite, TblCoiffeuse, TblClient, TblUser, TblServiceTemps, TblServicePrix, \
    TblPrix, TblTemps, TblService, TblSalon
from .services.geolocation_service import GeolocationService
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return HttpResponse("Bienvenue sur l'API Hairbnb!")


@csrf_exempt
# ++++++++++++++++++++++++++++++++++++++Importanbt+++++++++++++++++++++++++++++++++++++++++++++
#### ATTENTION : A MODIFIER : A ne pas laissé ainsi en production,
# car cela peut entrainer des attaques de type Cross-Site Scripting (XSS),
# ce qui pourrait permettre aux attaquants de injecter du code malveillant dans la page web.
# Donc ce qu'il faut changer a la production est de modifier le decorator csrf_exempt par @csrf_protect
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def create_user_profile(request):
    """
    Crée un profil utilisateur en fonction des données envoyées via une requête POST.
    """
    if request.method == 'POST':
        try:
            # Vérifiez si la requête contient des fichiers (multipart/form-data)
            if request.content_type.startswith('multipart/form-data'):
                # Utilisez request.POST et request.FILES
                data = request.POST
                photo_profil = request.FILES.get('photo_profil')
            else:
                # Sinon, lisez les données JSON dans request.body
                data = json.loads(request.body)
                photo_profil = None

            # Debugging: Afficher les données reçues
            print("Données reçues :", data)
            print("Fichiers reçus :", request.FILES)

            # Champs obligatoires pour tous les utilisateurs
            required_fields = [
                'userUuid', 'email', 'role', 'nom', 'prenom', 'sexe',
                'telephone', 'code_postal', 'commune', 'rue', 'numero', 'date_naissance'
            ]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"status": "error", "message": f"Le champ {field} est obligatoire."}, status=400)

            # Validation spécifique pour la date de naissance
            try:
                date_naissance = datetime.strptime(data['date_naissance'], '%d-%m-%Y').date()
            except ValueError:
                return JsonResponse(
                    {"status": "error", "message": "Le format de la date de naissance doit être DD-MM-YYYY."},
                    status=400,
                )

            # Vérifier si l'utilisateur existe déjà
            user_uuid = data['userUuid']
            if TblUser.objects.filter(uuid=user_uuid).exists():
                return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)

            # Étape 2 : Gérer l'adresse
            localite, _ = TblLocalite.objects.get_or_create(
                commune=data['commune'], code_postal=data['code_postal']
            )
            rue_obj, _ = TblRue.objects.get_or_create(nom_rue=data['rue'], localite=localite)
            adresse = TblAdresse.objects.create(
                numero=data['numero'], boite_postale=data.get('boite_postale', None), rue=rue_obj
            )

            # Étape 3 : Calculer les coordonnées géographiques avec le service
            adresse_complete = f"{data['numero']}, {data['rue']}, {data['commune']}, {data['code_postal']}"
            latitude, longitude = GeolocationService.geocode_address(adresse_complete)

            # Étape 4 : Créer un utilisateur de base
            user = TblUser.objects.create(
                uuid=user_uuid,
                nom=data['nom'],
                prenom=data['prenom'],
                email=data['email'],
                type=data['role'],
                sexe=data['sexe'],
                numero_telephone=data['telephone'],
                adresse=adresse,
                date_naissance=date_naissance,
                photo_profil=photo_profil  # Ajouter la photo de profil si elle existe
            )

            # Étape 5 : Gérer les rôles spécifiques
            if data['role'] == 'coiffeuse':
                TblCoiffeuse.objects.create(
                    idTblUser=user,
                    denomination_sociale=data.get('denomination_sociale'),
                    tva=data.get('tva'),
                    position=f"{latitude}, {longitude}" if latitude and longitude else None,

                )
            elif data['role'] == 'client':
                TblClient.objects.create(
                    idTblUser=user
                )

            # Réponse de succès
            return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)

        except Exception as e:
            # Gestion des erreurs générales
            print(f"Erreur : {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)

#*************************************************************************************************************


@csrf_exempt
def create_salon(request):
    """
    Crée un salon pour une coiffeuse en fonction des données envoyées via une requête POST.
    """
    if request.method == 'POST':
        try:
            # Déterminez si les données sont envoyées sous forme JSON ou via un formulaire (POST multipart)
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            # Ajoutez des logs pour vérifier les données reçues
            print("Requête reçue :", data)
            print("Fichiers reçus :", request.FILES)

            # Champs obligatoires
            user_uuid = data.get('userUuid')
            slogan = data.get('slogan')
            logo = request.FILES.get('logo_salon')  # Fichier logo

            print("UUID :", user_uuid)
            print("Slogan :", slogan)
            print("Logo :", logo)

            # Validez la présence des champs obligatoires
            if not user_uuid or not slogan:
                return JsonResponse(
                    {"status": "error", "message": "UUID utilisateur et slogan sont obligatoires"},
                    status=400
                )

            # Vérifiez si l'utilisateur existe
            user = TblUser.objects.filter(uuid=user_uuid, type='coiffeuse').first()
            if not user:
                return JsonResponse(
                    {"status": "error", "message": "Utilisateur introuvable ou non autorisé"},
                    status=404
                )

            # Créez ou mettez à jour le salon pour la coiffeuse
            coiffeuse, created = TblCoiffeuse.objects.update_or_create(
                idTblUser=user,
                defaults={
                    'slogan': slogan,
                    'logo_salon': logo
                }
            )

            if created:
                print(f"Salon créé pour la coiffeuse {user.nom} {user.prenom}")
            else:
                print(f"Salon mis à jour pour la coiffeuse {user.nom} {user.prenom}")

            return JsonResponse({"status": "success", "message": "Salon créé/mis à jour avec succès"}, status=201)

        except Exception as e:
            print(f"Erreur : {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)




@csrf_exempt
def add_or_update_service(request, service_id=None):
    if request.method in ['POST', 'PUT']:
        try:
            # Log le corps brut de la requête
            logging.info(f"Requête reçue avec le corps brut : {request.body}")

            # Décoder les données JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                logging.error("Erreur de décodage JSON.")
                return JsonResponse({'status': 'error', 'message': 'Format JSON invalide.'}, status=400)

            logging.info(f"Données JSON décodées : {data}")

            # Extraction des champs
            name = data.get('intitule_service') or data.get('name')
            description = data.get('description')
            minutes = data.get('temps_minutes') or data.get('minutes')
            price = data.get('prix') or data.get('price')

            logging.info(f"Champs extraits : name={name}, description={description}, minutes={minutes}, price={price}")

            # Vérification des champs obligatoires pour ajout
            if not service_id and not all([name, description, minutes, price]):
                logging.warning("Champs obligatoires manquants pour un nouveau service.")
                return JsonResponse({'status': 'error', 'message': 'Tous les champs sont obligatoires pour ajouter un nouveau service.'}, status=400)

            # Validation des types
            try:
                if minutes is not None:
                    minutes = int(minutes)
                if price is not None:
                    price = float(price)
            except ValueError:
                logging.warning("Minutes ou prix ont des valeurs invalides.")
                return JsonResponse({'status': 'error', 'message': 'Les champs minutes et prix doivent être numériques.'}, status=400)

            # Mise à jour
            if service_id:
                try:
                    service = TblService.objects.get(idTblService=service_id)
                except TblService.DoesNotExist:
                    logging.warning(f"Service avec ID {service_id} introuvable.")
                    return JsonResponse({'status': 'error', 'message': 'Service introuvable.'}, status=404)

                if name:
                    service.intitule_service = name
                if description:
                    service.description = description
                service.save()

                if minutes is not None:
                    TblServiceTemps.objects.filter(service=service).delete()
                    TblServiceTemps.objects.create(service=service, temps=TblTemps.objects.get_or_create(minutes=minutes)[0])
                if price is not None:
                    TblServicePrix.objects.filter(service=service).delete()
                    TblServicePrix.objects.create(service=service, prix=TblPrix.objects.get_or_create(prix=price)[0])

                logging.info("Service mis à jour avec succès.")
                return JsonResponse({'status': 'success', 'message': 'Service mis à jour avec succès.'}, status=200)

            # Ajout
            else:
                service = TblService.objects.create(
                    intitule_service=name,
                    description=description
                )
                TblServiceTemps.objects.create(service=service, temps=TblTemps.objects.create(minutes=minutes))
                TblServicePrix.objects.create(service=service, prix=TblPrix.objects.create(prix=price))

                logging.info("Nouveau service ajouté avec succès.")
                return JsonResponse({'status': 'success', 'message': 'Service ajouté avec succès.'}, status=201)

        except Exception as e:
            logging.error(f"Erreur serveur : {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Erreur serveur : {str(e)}'}, status=500)

    logging.warning("Méthode non autorisée.")
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def list_coiffeuses(request):
    """
    Vue pour lister les coiffeuses disponibles avec leurs informations détaillées.
    """
    if request.method == 'GET':
        try:
            # Récupérer toutes les coiffeuses actives avec les informations liées
            coiffeuses = TblCoiffeuse.objects.select_related('idTblUser').all()

            # Préparer les données pour la réponse JSON
            data = []
            for coiffeuse in coiffeuses:
                user = coiffeuse.idTblUser
                data.append({
                    'id': coiffeuse.id,  # ID de la coiffeuse
                    'uuid': user.uuid,  # UUID de l'utilisateur
                    'nom': user.nom,
                    'prenom': user.prenom,
                    'email': user.email,
                    'numero_telephone': user.numero_telephone,
                    'photo_profil': user.photo_profil.url if user.photo_profil else None,
                    'denomination_sociale': coiffeuse.denomination_sociale,
                    'tva': coiffeuse.tva,
                    'position': coiffeuse.position,
                })

            return JsonResponse({'status': 'success', 'data': data}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def coiffeuse_services(request, coiffeuse_id):
    try:
        # Vérifier si le salon existe pour la coiffeuse
        salon = TblSalon.objects.get(coiffeuse_id=coiffeuse_id)

        # Récupérer tous les services du salon
        services = TblService.objects.filter(salons=salon).distinct().values(
            'idTblService',
            'intitule_service',
            'description',
        )

        # Ajouter les relations avec temps et prix
        services_with_details = []
        for service in services:
            service_id = service['idTblService']

            # Récupérer la durée (temps)
            service_temps = TblServiceTemps.objects.filter(service_id=service_id).first()
            minutes = service_temps.temps.minutes if service_temps else None

            # Récupérer le prix
            service_prix = TblServicePrix.objects.filter(service_id=service_id).first()
            price = service_prix.prix.prix if service_prix else None

            # Ajouter les détails au service
            service['temps_minutes'] = minutes
            service['prix'] = price

            services_with_details.append(service)

        return JsonResponse(services_with_details, safe=False, status=200)
    except TblSalon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Salon introuvable pour cette coiffeuse.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur serveur : {str(e)}'}, status=500)



# def coiffeuse_services(request, coiffeuse_id):
#     try:
#         coiffeuse = TblCoiffeuse.objects.get(id=coiffeuse_id)
#         services = TblService.objects.filter(salon__coiffeuse=coiffeuse)
#         data = [{"idTblService": service.idTblService, "intitule_service": service.intitule_service, "description": service.description, "prix": service.prix.prix if service.prix else None, "temps_minutes": service.temps.minutes if service.temps else None} for service in services]
#         return JsonResponse(data, safe=False)
#     except TblCoiffeuse.DoesNotExist:
#         return JsonResponse({"status": "error", "message": "Coiffeuse introuvable"}, status=404)

@csrf_exempt
def ServicesListView(request):
    if request.method == 'GET':
        services = TblService.objects.all().values('idTblService', 'intitule_service', 'description')
        return JsonResponse(list(services), safe=False)





# @csrf_exempt
# def add_or_update_service(request, service_id=None):
#     if request.method == 'POST' or request.method == 'PUT':
#         try:
#             data = json.loads(request.body)
#
#             name = data.get('intitule_service')
#             description = data.get('description')
#             minutes = data.get('temps_minutes')
#             price = data.get('prix')
#
#             # Vérification des champs obligatoires
#             if not name or not description or not minutes or not price:
#                 return JsonResponse({'status': 'error', 'message': 'Tous les champs sont obligatoires.'}, status=400)
#
#             # Mise à jour d'un service existant
#             if service_id:
#                 try:
#                     service = TblService.objects.get(idTblService=service_id)
#                 except TblService.DoesNotExist:
#                     return JsonResponse({'status': 'error', 'message': 'Service introuvable.'}, status=404)
#
#                 service.intitule_service = name
#                 service.description = description
#                 service.save()
#
#                 temps, _ = TblTemps.objects.get_or_create(minutes=int(minutes))
#                 prix, _ = TblPrix.objects.get_or_create(prix=float(price))
#
#                 TblServiceTemps.objects.filter(service=service).delete()
#                 TblServiceTemps.objects.create(service=service, temps=temps)
#
#                 TblServicePrix.objects.filter(service=service).delete()
#                 TblServicePrix.objects.create(service=service, prix=prix)
#
#                 return JsonResponse({'status': 'success', 'message': 'Service mis à jour avec succès.'}, status=200)
#
#             # Ajout d'un nouveau service
#             else:
#                 temps = TblTemps.objects.create(minutes=int(minutes))
#                 prix = TblPrix.objects.create(prix=float(price))
#                 service = TblService.objects.create(
#                     intitule_service=name,
#                     description=description
#                 )
#                 TblServiceTemps.objects.create(service=service, temps=temps)
#                 TblServicePrix.objects.create(service=service, prix=prix)
#
#                 return JsonResponse({'status': 'success', 'message': 'Service ajouté avec succès.'}, status=201)
#
#         except Exception as e:
#             logging.error(f"Erreur serveur : {str(e)}")
#             return JsonResponse({'status': 'error', 'message': f'Erreur serveur : {str(e)}'}, status=500)
#
#     return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)



# @csrf_exempt
# def create_salon(request):
#     if request.method == 'POST':
#         try:
#             # Vérifiez si la requête est de type JSON ou multipart
#             if request.content_type == 'application/json':
#                 # Parsez le corps JSON
#                 data = json.loads(request.body)
#                 user_uuid = data.get('userUuid')
#                 slogan = data.get('slogan')
#                 logo = None  # Les fichiers ne peuvent pas être envoyés via JSON
#             else:
#                 # Sinon, récupérez les données depuis POST et FILES
#                 user_uuid = request.POST.get('userUuid')
#                 slogan = request.POST.get('slogan')
#                 logo = request.FILES.get('logo')
#
#             # Affichez les données reçues pour déboguer
#             print("UUID :", user_uuid)
#             print("Slogan :", slogan)
#             print("Logo :", logo)
#
#             # Vérifiez les champs obligatoires
#             if not user_uuid or not slogan:
#                 return JsonResponse({"status": "error", "message": "UUID utilisateur et slogan sont obligatoires"}, status=400)
#
#             # Vérifiez si l'utilisateur existe
#             try:
#                 user = TblUser.objects.get(uuid=user_uuid, type="coiffeuse")
#             except TblUser.DoesNotExist:
#                 return JsonResponse({"status": "error", "message": "Utilisateur non trouvé ou non une coiffeuse"}, status=404)
#
#             # Créez ou mettez à jour le salon
#             salon, created = TblCoiffeuse.objects.update_or_create(
#                 idTblUser=user,
#                 defaults={
#                     'denomination_sociale': slogan,
#                     'logo_salon': logo,  # Peut être None si pas envoyé
#                 }
#             )
#
#             #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             print("Requête reçue :", request.POST)
#             print("UUID utilisateur :", data['userUuid'])
#             print("Slogan :", data['slogan'])
#             print("Fichier reçu :", request.FILES.get('logo_salon'))
#             #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#             message = "Salon créé" if created else "Salon mis à jour"
#             return JsonResponse({"status": "success", "message": message}, status=201)
#
#         except Exception as e:
#             print(f"Erreur : {str(e)}")
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)













# def create_user_profile(request):
#     """
#     Crée un profil utilisateur en fonction des données envoyées via une requête POST.
#     """
#     if request.method == 'POST':
#         try:
#
#             print("Données POST :", request.POST)  # Affiche les données envoyées sous forme de formulaire
#             print("Données JSON :", request.body)  # Affiche les données brutes de la requête
#             print("Fichiers reçus :", request.FILES)  # Affiche les fichiers envoyés
#
#             # Étape 1 : Récupérer les données de la requête JSON
#             if request.content_type == "application/json":
#                 data = json.loads(request.body)
#             else:
#                 data = request.POST
#
#             # Champs obligatoires pour tous les utilisateurs
#             required_fields = [
#                 'userUuid', 'email', 'role', 'nom', 'prenom', 'sexe',
#                 'telephone', 'code_postal', 'commune', 'rue', 'numero', 'date_naissance'
#             ]
#             for field in required_fields:
#                 value = data.get(field)
#                 if not value or str(value).strip().lower() == "null":
#                     return JsonResponse({"status": "error", "message": f"Le champ {field} est obligatoire."}, status=400)
#
#             # Validation spécifique pour la date de naissance
#             date_naissance = data.get('date_naissance')
#             try:
#                 # Convertir la date au format attendu (d-m-Y)
#                 parsed_date_naissance = datetime.strptime(date_naissance, '%d-%m-%Y').date()
#             except ValueError:
#                 return JsonResponse(
#                     {"status": "error", "message": "Le format de la date de naissance doit être DD-MM-YYYY."},status=400)
#
#             # Vérifier si l'utilisateur existe déjà
#             user_uuid = data.get('userUuid')
#             if TblUser.objects.filter(uuid=user_uuid).exists():
#                 return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)
#
#             # Étape 2 : Gérer l'adresse
#             localite, _ = TblLocalite.objects.get_or_create(
#                 commune=data['commune'], code_postal=data['code_postal']
#             )
#             rue_obj, _ = TblRue.objects.get_or_create(nom_rue=data['rue'], localite=localite)
#             adresse = TblAdresse.objects.create(
#                 numero=data['numero'], boite_postale=data.get('boite_postale', None), rue=rue_obj
#             )
#
#             # Étape 3 : Calculer les coordonnées géographiques avec le service
#             adresse_complete = f"{data['numero']}, {data['rue']}, {data['commune']}, {data['code_postal']}"
#             latitude, longitude = GeolocationService.geocode_address(adresse_complete)
#
#             # Étape 4 : Gérer les photos (photo_profil et logo_salon)
#             photo_profil = request.FILES.get('photo_profil')  # None si aucun fichier envoyé
#             if not photo_profil:
#                 print("Aucune photo_profil envoyée, utilisation de l'avatar par défaut.")
#             logo_salon = request.FILES.get('logo_salon')  # Fichier uploadé ou None
#             if logo_salon:
#                 print(f"Logo salon reçu : {logo_salon.name}, Taille : {logo_salon.size}")
#             else:
#                 print("Aucun logo_salon reçu, logo par défaut utilisé.")
#
#
#             # Étape 5 : Créer un utilisateur de base
#             user = TblUser.objects.create(
#                 uuid=user_uuid,
#                 nom=data['nom'],
#                 prenom=data['prenom'],
#                 email=data['email'],
#                 type=data['role'],
#                 sexe=data['sexe'],
#                 numero_telephone=data['telephone'],
#                 adresse=adresse,
#                 date_naissance=parsed_date_naissance,  # Ajout de la date de naissance
#                 photo_profil=photo_profil  # Ajouter la photo de profil
#             )
#
#             # Étape 5 : Créer un enregistrement spécifique selon le rôle
#             if data['role'] == 'coiffeuse':
#                 TblCoiffeuse.objects.create(
#                     idTblUser=user,
#                     denomination_sociale=data.get('denomination_sociale', None),
#                     tva=data.get('tva', None),
#                     position=f"{latitude}, {longitude}" if latitude and longitude else None,
#                     logo_salon=logo_salon  # Ajouter le logo du salon
#                 )
#             elif data['role'] == 'client':
#                 TblClient.objects.create(
#                     idTblUser=user
#                 )
#
#             return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)
#
#         except Exception as e:
#             print(f"Erreur : {str(e)}")
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)







# def create_user_profile(request):
#     """
#     Crée un profil utilisateur en fonction des données envoyées via une requête POST.
#     """
#     if request.method == 'POST':
#         try:
#             # Étape 1 : Récupérer les données de la requête JSON
#             data = json.loads(request.body)
#             user_uuid = data.get('userUuid')
#             email = data.get('email')
#
#             # Validation des champs obligatoires pour tous les utilisateurs
#             required_fields = [
#                 'userUuid', 'email', 'role', 'nom', 'prenom', 'sexe',
#                 'telephone', 'code_postal', 'commune', 'rue', 'numero', 'date_naissance'
#             ]
#             for field in required_fields:
#                 if not data.get(field):
#                     return JsonResponse({"status": "error", "message": f"Le champ {field} est obligatoire."}, status=400)
#
#                     # Validation spécifique pour la date de naissance
#                     date_naissance = data.get('date_naissance')
#                     try:
#                         # Convertir la date au format attendu (YYYY-MM-DD)
#                         parsed_date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d').date()
#                     except ValueError:
#                         return JsonResponse(
#                             {"status": "error", "message": "Le format de la date de naissance doit être YYYY-MM-DD."},
#                             status=400)
#
#             # Validation spécifique au rôle
#             role = data.get('role')  # 'client' ou 'coiffeuse'
#             if role == 'coiffeuse':
#                 # Champs spécifiques pour les coiffeuses
#                 coiffeuse_fields = ['denomination_sociale', 'tva']
#                 for field in coiffeuse_fields:
#                     if not data.get(field):
#                         return JsonResponse({"status": "error", "message": f"Le champ {field} est obligatoire pour les coiffeuses."}, status=400)
#             elif role != 'client':
#                 return JsonResponse({"status": "error", "message": "Rôle non valide."}, status=400)
#
#             # Vérifier si l'utilisateur existe déjà
#             if TblUser.objects.filter(uuid=user_uuid).exists():
#                 return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)
#
#             # Récupération des données principales
#             nom = data.get('nom')
#             prenom = data.get('prenom')
#             sexe = data.get('sexe')
#             telephone = data.get('telephone')
#             code_postal = data.get('code_postal')
#             commune = data.get('commune')
#             rue = data.get('rue')
#             numero = data.get('numero')
#             boite_postale = data.get('boite_postale', None)
#
#             # Étape 2 : Gérer l'adresse
#             localite, _ = TblLocalite.objects.get_or_create(
#                 commune=commune, code_postal=code_postal
#             )
#             rue_obj, _ = TblRue.objects.get_or_create(nom_rue=rue, localite=localite)
#             adresse = TblAdresse.objects.create(
#                 numero=numero, boite_postale=boite_postale, rue=rue_obj
#             )
#
#             # Étape 3 : Calculer les coordonnées géographiques avec le service
#             adresse_complete = f"{numero}, {rue}, {commune}, {code_postal}"
#             latitude, longitude = GeolocationService.geocode_address(adresse_complete)
#
#             # Étape 4 : Créer un utilisateur de base
#             user = TblUser.objects.create(
#                 uuid=user_uuid,
#                 nom=nom,
#                 prenom=prenom,
#                 email=email,
#                 type=role,
#                 sexe=sexe,
#                 numero_telephone=telephone,
#                 adresse=adresse,
#                 date_naissance=parsed_date_naissance,  # Ajout de la date de naissance
#             )
#
#             # Étape 5 : Créer un enregistrement spécifique selon le rôle
#             if role == 'coiffeuse':
#                 TblCoiffeuse.objects.create(
#                     idTblUser=user,
#                     denomination_sociale=data.get('denomination_sociale', None),
#                     tva=data.get('tva', None),
#                     position=f"{latitude}, {longitude}" if latitude and longitude else None,
#                 )
#             elif role == 'client':
#                 TblClient.objects.create(
#                     idTblUser=user
#                 )
#
#             return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)
#
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)


# def create_user_profile(request):
#     """
#     Crée un profil utilisateur en fonction des données envoyées via une requête POST.
#     """
#     if request.method == 'POST':
#         try:
#             # Étape 1 : Récupérer les données de la requête JSON
#             data = json.loads(request.body)
#             user_uuid = data.get('userUuid')
#             email = data.get('email')
#
#             # Vérifier si l'utilisateur existe déjà
#             if TblUser.objects.filter(uuid=user_uuid).exists():
#                 return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)
#
#
#
#             # Récupération des données principales
#             role = data.get('role')  # 'client' ou 'coiffeuse'
#             nom = data.get('nom')
#             prenom = data.get('prenom')
#             sexe = data.get('sexe')
#             telephone = data.get('telephone')
#             code_postal = data.get('code_postal')
#             commune = data.get('commune')
#             rue = data.get('rue')
#             numero = data.get('numero')
#             boite_postale = data.get('boite_postale', None)
#
#             # Étape 2 : Gérer l'adresse
#             localite, _ = TblLocalite.objects.get_or_create(
#                 commune=commune, code_postal=code_postal
#             )
#             rue_obj, _ = TblRue.objects.get_or_create(nom_rue=rue, localite=localite)
#             adresse = TblAdresse.objects.create(
#                 numero=numero, boite_postale=boite_postale, rue=rue_obj
#             )
#
#             # Étape 3 : Calculer les coordonnées géographiques avec le service
#             adresse_complete = f"{numero}, {rue}, {commune}, {code_postal}"
#             latitude, longitude = GeolocationService.geocode_address(adresse_complete)
#
#             # Étape 4 : Créer un utilisateur de base
#             user = TblUser.objects.create(
#                 uuid=user_uuid,
#                 nom=nom,
#                 prenom=prenom,
#                 email=email,
#                 type=role,
#                 sexe=sexe,
#                 numero_telephone=telephone,
#                 adresse=adresse,
#             )
#             # Étape 5 : Créer un enregistrement spécifique selon le rôle
#             if role == 'coiffeuse':
#                 TblCoiffeuse.objects.create(
#                     idTblUser=user,
#                     denomination_sociale=data.get('denomination_sociale', None),
#                     tva=data.get('tva', None),
#                     position=f"{latitude}, {longitude}" if latitude and longitude else None,
#                 )
#             elif role == 'client':
#                 TblClient.objects.create(
#                     idTblUser=user
#                 )
#             else:
#                 return JsonResponse({"status": "error", "message": "Rôle non valide"}, status=400)
#
#             return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)
#
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)

# def create_user_profile(request):
#     if request.method == 'POST':
#         try:
#             # Étape 1 : Récupérer les données de la requête JSON
#             data = json.loads(request.body)
#             user_uuid = data.get('userUuid')
#             email = data.get('email')
#
#             # Vérifier si l'utilisateur existe déjà
#             if TblUser.objects.filter(uuid=user_uuid).exists():
#                 return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)
#
#             # Récupération des données principales
#             role = data.get('role')  # 'client' ou 'coiffeuse'
#             nom = data.get('nom')
#             prenom = data.get('prenom')
#             sexe = data.get('sexe')
#             telephone = data.get('telephone')
#             code_postal = data.get('code_postal')
#             commune = data.get('commune')
#             rue = data.get('rue')
#             numero = data.get('numero')
#             boite_postale = data.get('boite_postale')
#
#             # Étape 2 : Gérer l'adresse
#             localite, _ = TblLocalite.objects.get_or_create(
#                 commune=commune, code_postal=code_postal
#             )
#             rue_obj, _ = TblRue.objects.get_or_create(nom_rue=rue, localite=localite)
#             adresse = TblAdresse.objects.create(numero=numero, boite_postale=boite_postale, rue=rue_obj)
#
#             # Étape 3 : Créer un utilisateur de base
#             user = TblUser.objects.create(
#                 uuid=user_uuid,
#                 nom=nom,
#                 prenom=prenom,
#                 email=email,
#                 type=role,
#                 sexe=sexe,
#                 numero_telephone=telephone,
#                 adresse=adresse,
#             )
#
#             # Étape 4 : Créer un enregistrement spécifique selon le rôle
#             if role == 'coiffeuse':
#                 denomination_sociale = data.get('denomination_sociale')
#                 tva = data.get('tva')
#
#                 TblCoiffeuse.objects.create(
#                     uuid=user_uuid,
#                     nom=nom,
#                     prenom=prenom,
#                     email=email,
#                     type=role,
#                     sexe=sexe,
#                     numero_telephone=telephone,
#                     adresse=adresse,
#                     denomination_sociale=denomination_sociale,
#                     tva=tva
#                 )
#             elif role == 'client':
#                 TblClient.objects.create(
#                     uuid=user_uuid,
#                     nom=nom,
#                     prenom=prenom,
#                     email=email,
#                     type=role,
#                     sexe=sexe,
#                     numero_telephone=telephone,
#                     adresse=adresse
#                 )
#
#             return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)
#
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)




# ++++++++++++++++++++++++++++++++++++++Explication+++++++++++++++++++++++++++++++++++++++++++++
# Cette vue verifie si un utilisateur existe ou non dans la bd
# Le but est de savoir s'il faut afficher la page pour creer le profil ou non
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@csrf_exempt  # À modifier en production (utiliser @csrf_protect)
def check_user_profile(request):
    if request.method == 'POST':  # Accepter uniquement la méthode POST
        try:
            # Charger les données JSON envoyées
            data = json.loads(request.body)
            user_uuid = data.get('userUuid')

            # Vérifier si l'utilisateur existe avec cet UUID
            user_exists = TblUser.objects.filter(uuid=user_uuid).exists()

            if user_exists:
                return JsonResponse({"status": "exists"}, status=200)
            else:
                return JsonResponse({"status": "not_exists"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)

