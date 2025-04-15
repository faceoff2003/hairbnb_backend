from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from hairbnb.models import TblUser, TblCoiffeuse, TblSalon
from hairbnb.serializers.salon_services_serializers import TblSalonSerializer, TblSalonImageSerializer


@api_view(['POST'])
def ajout_salon_serializer_view(request):
    """
    Crée un salon pour une coiffeuse.
    Reçoit : idTblUser, nom_salon, slogan, logo_salon
    Renvoie : salon_id
    """
    try:
        # 🔥 Récupération des champs
        user_id = request.data.get('idTblUser')
        nom_salon = request.data.get('nom_salon')
        slogan = request.data.get('slogan')
        logo = request.FILES.get('logo_salon')

        # 🔒 Vérification des champs obligatoires
        if not user_id or not nom_salon or not slogan or not logo:
            return Response({
                "status": "error",
                "message": "Champs requis : idTblUser, nom_salon, slogan, logo_salon"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🔍 Vérification de l'utilisateur coiffeuse
        user = TblUser.objects.filter(idTblUser=user_id, type='coiffeuse').first()
        if not user:
            return Response({
                "status": "error",
                "message": "Utilisateur introuvable ou non autorisé (type != coiffeuse)"
            }, status=status.HTTP_404_NOT_FOUND)

        # 🔍 Vérification de la coiffeuse liée
        coiffeuse = TblCoiffeuse.objects.filter(idTblUser=user).first()
        if not coiffeuse:
            return Response({
                "status": "error",
                "message": "Coiffeuse introuvable pour cet utilisateur"
            }, status=status.HTTP_404_NOT_FOUND)

        # 🚫 Vérifie qu’elle n’a pas déjà un salon
        if TblSalon.objects.filter(coiffeuse=coiffeuse).exists():
            return Response({
                "status": "error",
                "message": "Un salon existe déjà pour cette coiffeuse"
            }, status=status.HTTP_409_CONFLICT)

        # 📦 Préparation des données pour le serializer
        data = {
            "coiffeuse": coiffeuse.id,
            "nom_salon": nom_salon,
            "slogan": slogan,
            "logo_salon": logo
        }

        serializer = TblSalonSerializer(data=data)
        if serializer.is_valid():
            salon = serializer.save()
            return Response({
                "status": "success",
                "message": "Salon créé avec succès",
                "salon_id": salon.idTblSalon
            }, status=status.HTTP_201_CREATED)

        # ❌ Si invalide
        return Response({
            "status": "error",
            "message": "Données invalides",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print("🔥 Erreur lors de la création du salon :", str(e))
        return Response({
            "status": "error",
            "message": "Erreur serveur",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def ajout_salon_serializer_view(request):
#     """
#     Crée un salon pour une coiffeuse.
#     Reçoit : idTblUser, nom_salon, slogan, logo_salon
#     Renvoie : salon_id
#     """
#     user_id = request.data.get('idTblUser')
#     nom_salon = request.data.get('nom_salon')
#     slogan = request.data.get('slogan')
#     logo = request.FILES.get('logo_salon')
#
#     # 🔒 Vérification des champs obligatoires
#     if not user_id or not nom_salon or not slogan or not logo:
#         return Response(
#             {"status": "error", "message": "Champs requis : idTblUser, nom_salon, slogan, logo_salon"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # 🔍 Recherche de l'utilisateur
#     user = TblUser.objects.filter(id=user_id, type='coiffeuse').first()
#     if not user:
#         return Response(
#             {"status": "error", "message": "Utilisateur introuvable ou non autorisé"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#
#     # 🔍 Recherche de la coiffeuse
#     coiffeuse = TblCoiffeuse.objects.filter(idTblUser=user).first()
#     if not coiffeuse:
#         return Response(
#             {"status": "error", "message": "Coiffeuse introuvable"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#
#     # ✅ Vérifie qu’un seul salon est autorisé
#     if TblSalon.objects.filter(coiffeuse=coiffeuse).exists():
#         return Response(
#             {"status": "error", "message": "Un salon existe déjà pour cette coiffeuse"},
#             status=status.HTTP_409_CONFLICT
#         )
#
#     # 📦 Préparer les données pour le serializer
#     data = {
#         "coiffeuse": coiffeuse.id,
#         "nom_salon": nom_salon,
#         "slogan": slogan,
#         "logo_salon": logo
#     }
#
#     serializer = TblSalonSerializer(data=data)
#     if serializer.is_valid():
#         salon = serializer.save()
#         return Response({
#             "status": "success",
#             "message": "Salon créé avec succès",
#             "salon_id": salon.idTblSalon
#         }, status=status.HTTP_201_CREATED)
#
#     return Response({
#         "status": "error",
#         "message": "Données invalides",
#         "errors": serializer.errors
#     }, status=status.HTTP_400_BAD_REQUEST)




# @api_view(['POST'])
# def ajout_salon_serializer_view(request):
#     """
#     Crée un salon pour une coiffeuse.
#     Reçoit : userUuid, nom_salon, slogan, logo_salon
#     Renvoie : salon_id
#     """
#     user_uuid = request.data.get('userUuid')
#     nom_salon = request.data.get('nom_salon')
#     slogan = request.data.get('slogan')
#     logo = request.FILES.get('logo_salon')
#
#     # 🔒 Vérification des champs obligatoires
#     if not user_uuid or not nom_salon or not slogan or not logo:
#         return Response(
#             {"status": "error", "message": "Champs requis : userUuid, nom_salon, slogan, logo_salon"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # 🔍 Recherche de l'utilisateur
#     user = TblUser.objects.filter(uuid=user_uuid, type='coiffeuse').first()
#     if not user:
#         return Response(
#             {"status": "error", "message": "Utilisateur introuvable ou non autorisé"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#
#     # 🔍 Recherche de la coiffeuse
#     coiffeuse = TblCoiffeuse.objects.filter(idTblUser=user).first()
#     if not coiffeuse:
#         return Response(
#             {"status": "error", "message": "Coiffeuse introuvable"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#
#     # ✅ Vérifie qu’un seul salon est autorisé
#     if TblSalon.objects.filter(coiffeuse=coiffeuse).exists():
#         return Response(
#             {"status": "error", "message": "Un salon existe déjà pour cette coiffeuse"},
#             status=status.HTTP_409_CONFLICT
#         )
#
#     # 📦 Préparer les données pour le serializer
#     data = {
#         "coiffeuse": coiffeuse.id,
#         "nom_salon": nom_salon,
#         "slogan": slogan,
#         "logo_salon": logo
#     }
#
#     serializer = TblSalonSerializer(data=data)
#     if serializer.is_valid():
#         salon = serializer.save()
#         return Response({
#             "status": "success",
#             "message": "Salon créé avec succès",
#             "salon_id": salon.idTblSalon
#         }, status=status.HTTP_201_CREATED)
#
#     return Response({
#         "status": "error",
#         "message": "Données invalides",
#         "errors": serializer.errors
#     }, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_salon_by_coiffeuse(request, coiffeuse_id):
#     """
#     Vérifie si un salon existe pour une coiffeuse donnée.
#     Retourne les données si trouvé, sinon un flag exists: False
#     """
#     try:
#         salon = TblSalon.objects.get(coiffeuse_id=coiffeuse_id)
#         serializer = TblSalonSerializer(salon)
#         return Response({
#             "exists": True,
#             "salon": serializer.data
#         }, status=status.HTTP_200_OK)
#     except TblSalon.DoesNotExist:
#         return Response({
#             "exists": False,
#             "message": "Aucun salon trouvé pour cette coiffeuse."
#         }, status=status.HTTP_200_OK)

@csrf_exempt
def get_salon_by_coiffeuse(request, coiffeuse_id):
    try:
        coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
        salon = TblSalon.objects.get(coiffeuse=coiffeuse)

        salon_data = {
            "idTblSalon": salon.idTblSalon,
            "coiffeuse": coiffeuse.idTblUser.idTblUser,
            "nom_salon": salon.nom_salon,
            "slogan": salon.slogan,
            "logo_salon": salon.logo_salon.url if salon.logo_salon else None,
        }

        return JsonResponse({'exists': True, 'salon': salon_data})

    except TblCoiffeuse.DoesNotExist:
        return JsonResponse({'exists': False, 'message': "Coiffeuse introuvable"}, status=404)

    except TblSalon.DoesNotExist:
        return JsonResponse({'exists': False, 'message': "Salon introuvable"}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_images_to_salon(request):
    print("✅ La vue a bien été appelée !")
    salon_id = request.data.get('salon')
    images = request.FILES.getlist('image')

    print("🧪 Reçues images:", [img.name for img in images])

    if not salon_id or not images:
        return Response({"error": "Champs requis : salon, image(s)"}, status=status.HTTP_400_BAD_REQUEST)

    if len(images) < 3:
        return Response({"error": "Veuillez télécharger au moins 3 images."}, status=status.HTTP_400_BAD_REQUEST)

    if len(images) > 12:
        return Response({"error": "Vous ne pouvez pas télécharger plus de 12 images."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        salon = TblSalon.objects.get(idTblSalon=salon_id)
    except TblSalon.DoesNotExist:
        return Response({"error": "Salon introuvable."}, status=status.HTTP_404_NOT_FOUND)

    image_ids = []
    for img in images:
        print(f"-> Image: {img.name}, Taille: {img.size}")

        if img.size > 6 * 1024 * 1024:
            return Response(
                {"error": f"L'image '{img.name}' dépasse 6MB."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        # ✅ ICI : c'est bien le champ `salon` (ID) et `image` (fichier)
        serializer = TblSalonImageSerializer(data={
            "salon": int(salon_id),
            "image": img
        })

        if serializer.is_valid():
            instance = serializer.save()
            image_ids.append(instance.id)
        else:
            print("⛔ Serializer invalide:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"success": True, "image_ids": image_ids}, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def add_images_to_salon(request):
#     """
#     Ajoute une ou plusieurs images à un salon donné.
#     Reçoit : salon (ID), image (fichier image) – peut être multiple
#     Renvoie : liste des IDs des images créées
#     """
#     salon_id = request.data.get('salon')
#     images = request.FILES.getlist('image')
#
#     if not salon_id or not images:
#         return Response({"error": "Champs requis : salon, image(s)"}, status=status.HTTP_400_BAD_REQUEST)
#
#     if len(images) < 3:
#         return Response({"error": "Veuillez télécharger au moins 3 images."}, status=status.HTTP_400_BAD_REQUEST)
#
#     if len(images) > 12:
#         return Response({"error": "Vous ne pouvez pas télécharger plus de 12 images."}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         salon = TblSalon.objects.get(idTblSalon=salon_id)
#     except TblSalon.DoesNotExist:
#         return Response({"error": "Salon introuvable."}, status=status.HTTP_404_NOT_FOUND)
#
#     image_ids = []
#     for img in images:
#         if img.size > 6 * 1024 * 1024:  # 6MB
#             return Response({"error": f"L'image '{img.name}' dépasse 6MB."}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
#
#         serializer = TblSalonImageSerializer(data={"salon": salon.idTblSalon, "image": img})
#         if serializer.is_valid():
#             instance = serializer.save()
#             image_ids.append(instance.id)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     return Response({"success": True, "image_ids": image_ids}, status=status.HTTP_201_CREATED)

