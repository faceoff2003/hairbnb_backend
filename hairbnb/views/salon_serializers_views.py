from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from hairbnb.models import TblUser, TblCoiffeuse, TblSalon
from hairbnb.serializers.salon_services_serializers import TblSalonSerializer


@api_view(['POST'])
def ajout_salon_serializer_view(request):
    """
    Crée un salon pour une coiffeuse.
    Reçoit : userUuid, nom_salon, slogan, logo_salon
    Renvoie : salon_id
    """
    user_uuid = request.data.get('userUuid')
    nom_salon = request.data.get('nom_salon')
    slogan = request.data.get('slogan')
    logo = request.FILES.get('logo_salon')

    # 🔒 Vérification des champs obligatoires
    if not user_uuid or not nom_salon or not slogan or not logo:
        return Response(
            {"status": "error", "message": "Champs requis : userUuid, nom_salon, slogan, logo_salon"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔍 Recherche de l'utilisateur
    user = TblUser.objects.filter(uuid=user_uuid, type='coiffeuse').first()
    if not user:
        return Response(
            {"status": "error", "message": "Utilisateur introuvable ou non autorisé"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔍 Recherche de la coiffeuse
    coiffeuse = TblCoiffeuse.objects.filter(idTblUser=user).first()
    if not coiffeuse:
        return Response(
            {"status": "error", "message": "Coiffeuse introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ Vérifie qu’un seul salon est autorisé
    if TblSalon.objects.filter(coiffeuse=coiffeuse).exists():
        return Response(
            {"status": "error", "message": "Un salon existe déjà pour cette coiffeuse"},
            status=status.HTTP_409_CONFLICT
        )

    # 📦 Préparer les données pour le serializer
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

    return Response({
        "status": "error",
        "message": "Données invalides",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_salon_by_coiffeuse(request, coiffeuse_id):
    """
    Vérifie si un salon existe pour une coiffeuse donnée.
    Retourne les données si trouvé, sinon un flag exists: False
    """
    try:
        salon = TblSalon.objects.get(coiffeuse_id=coiffeuse_id)
        serializer = TblSalonSerializer(salon)
        return Response({
            "exists": True,
            "salon": serializer.data
        }, status=status.HTTP_200_OK)
    except TblSalon.DoesNotExist:
        return Response({
            "exists": False,
            "message": "Aucun salon trouvé pour cette coiffeuse."
        }, status=status.HTTP_200_OK)
