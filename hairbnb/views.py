from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TblAdresse, TblRue, TblLocalite, TblCoiffeuse, TblClient, TblUser


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
            # Étape 1 : Récupérer les données de la requête JSON
            data = json.loads(request.body)
            user_uuid = data.get('userUuid')
            email = data.get('email')

            # Vérifier si l'utilisateur existe déjà
            if TblUser.objects.filter(uuid=user_uuid).exists():
                return JsonResponse({"status": "error", "message": "Utilisateur déjà existant"}, status=400)

            # Récupération des données principales
            role = data.get('role')  # 'client' ou 'coiffeuse'
            nom = data.get('nom')
            prenom = data.get('prenom')
            sexe = data.get('sexe')
            telephone = data.get('telephone')
            code_postal = data.get('code_postal')
            commune = data.get('commune')
            rue = data.get('rue')
            numero = data.get('numero')
            boite_postale = data.get('boite_postale', None)

            # Étape 2 : Gérer l'adresse
            localite, _ = TblLocalite.objects.get_or_create(
                commune=commune, code_postal=code_postal
            )
            rue_obj, _ = TblRue.objects.get_or_create(nom_rue=rue, localite=localite)
            adresse = TblAdresse.objects.create(
                numero=numero, boite_postale=boite_postale, rue=rue_obj
            )

            # Étape 3 : Créer un utilisateur de base
            user = TblUser.objects.create(
                uuid=user_uuid,
                nom=nom,
                prenom=prenom,
                email=email,
                type=role,
                sexe=sexe,
                numero_telephone=telephone,
                adresse=adresse,
            )

            # Étape 4 : Créer un enregistrement spécifique selon le rôle
            if role == 'coiffeuse':
                denomination_sociale = data.get('denomination_sociale', None)
                tva = data.get('tva', None)

                # Crée une instance de TblCoiffeuse
                TblCoiffeuse.objects.create(
                    uuid=user_uuid,
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    type=role,
                    sexe=sexe,
                    numero_telephone=telephone,
                    adresse=adresse,
                    denomination_sociale=denomination_sociale,
                    tva=tva,
                )
            elif role == 'client':
                # Crée une instance de TblClient
                TblClient.objects.create(
                    uuid=user_uuid,
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    type=role,
                    sexe=sexe,
                    numero_telephone=telephone,
                    adresse=adresse,
                )
            else:
                return JsonResponse({"status": "error", "message": "Rôle non valide"}, status=400)

            return JsonResponse({"status": "success", "message": "Profil créé avec succès!"}, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)

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

