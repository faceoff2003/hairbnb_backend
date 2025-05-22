from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from hairbnb.models import TblUser, TblCoiffeuse, TblSalon
from hairbnb.salon.salon_serializers import TblSalonSerializer


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

# @csrf_exempt
# def get_salon_by_coiffeuse(request, coiffeuse_id):
#     try:
#         coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
#         salon = TblSalon.objects.get(coiffeuse=coiffeuse)
#
#         salon_data = {
#             "idTblSalon": salon.idTblSalon,
#             "coiffeuse": coiffeuse.idTblUser.idTblUser,
#             "nom_salon": salon.nom_salon,
#             "slogan": salon.slogan,
#             "logo_salon": salon.logo_salon.url if salon.logo_salon else None,
#         }
#
#         return JsonResponse({'exists': True, 'salon': salon_data})
#
#     except TblCoiffeuse.DoesNotExist:
#         return JsonResponse({'exists': False, 'message': "Coiffeuse introuvable"}, status=404)
#
#     except TblSalon.DoesNotExist:
#         return JsonResponse({'exists': False, 'message': "Salon introuvable"}, status=404)
#
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
