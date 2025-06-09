from django.http import JsonResponse

from decorators.decorators import firebase_authenticated
from hairbnb.models import TblSalon, TblCoiffeuseSalon
from math import radians, cos, sin, sqrt, atan2

from hairbnb.salon_geolocalisation.salon_geolocalisation_serializers import SalonSerializer


def haversine(lat1, lon1, lat2, lon2):
    """
    Calcul de la distance entre deux points en kilomètres avec la formule de Haversine.
    """
    R = 6371  # Rayon moyen de la Terre en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@firebase_authenticated
def salons_proches(request):
    """
    Récupère les salons proches d'une position donnée selon une distance max.
    Nécessite une authentification Firebase.
    """
    try:
        # Récupération des paramètres
        lat_client = float(request.GET.get('lat', 0))  # Latitude du client
        lon_client = float(request.GET.get('lon', 0))  # Longitude du client
        distance_max = float(request.GET.get('distance', 10))  # Distance max en km

        # Liste pour stocker les salons proches
        salons = []

        # Parcourir tous les salons
        for salon in TblSalon.objects.all():
            if salon.position and salon.position != "0,0":
                try:
                    # Extraire coordonnées du salon
                    lat_salon, lon_salon = map(float, salon.position.split(","))

                    # Calculer la distance
                    distance = haversine(lat_client, lon_client, lat_salon, lon_salon)

                    # Si le salon est dans le rayon demandé
                    if distance <= distance_max:
                        # Stocker la distance comme attribut temporaire
                        salon.distance = round(distance, 2)
                        salons.append(salon)
                except ValueError:
                    print(f"⚠️ Erreur conversion position pour salon {salon.nom_salon}")

        # Trier les salons par distance
        salons.sort(key=lambda s: getattr(s, 'distance', float('inf')))

        # Créer une liste pour stocker les résultats sérialisés
        serialized_data = []

        # Sérialiser chaque salon et ajouter la distance
        for salon in salons:
            salon_data = SalonSerializer(salon).data
            salon_data['distance'] = getattr(salon, 'distance', 0)
            serialized_data.append(salon_data)

        # Retourner la réponse JSON
        return JsonResponse({
            "status": "success",
            "count": len(salons),
            "salons": serialized_data
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@firebase_authenticated
def get_salon_details(request, salon_id):
    """
    Récupère les détails d'un salon spécifique.
    Nécessite une authentification Firebase.
    """
    try:
        # Récupérer le salon
        salon = TblSalon.objects.get(idTblSalon=salon_id)

        # Sérialiser le salon
        salon_data = SalonSerializer(salon).data

        # Récupérer les détails des coiffeuses qui travaillent dans ce salon
        coiffeuses_data = []
        relations = TblCoiffeuseSalon.objects.filter(salon=salon)

        for relation in relations:
            coiffeuse = relation.coiffeuse
            user = coiffeuse.idTblUser

            coiffeuses_data.append({
                "idTblCoiffeuse": coiffeuse.idTblUser.idTblUser,
                "nom": user.nom,
                "prenom": user.prenom,
                "photo_profil": request.build_absolute_uri(user.photo_profil.url) if user.photo_profil else None,
                "est_proprietaire": relation.est_proprietaire,
                "nom_commercial": coiffeuse.nom_commercial
            })

        # Ajouter les informations des coiffeuses au salon
        salon_data['coiffeuses_details'] = coiffeuses_data

        return JsonResponse({
            "status": "success",
            "salon": salon_data
        })

    except TblSalon.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Salon non trouvé"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


def get_all_salons(request):
    """
    Récupère tous les salons disponibles.
    """
    try:
        # Récupérer tous les salons
        salons = TblSalon.objects.all()
        
        # Sérialiser tous les salons
        serialized_data = []
        for salon in salons:
            salon_data = SalonSerializer(salon).data
            serialized_data.append(salon_data)
        
        return JsonResponse({
            "status": "success",
            "count": len(salons),
            "salons": serialized_data
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)