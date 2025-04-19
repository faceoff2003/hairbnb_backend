from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SalonDetailSerializer
from ..models import TblSalon


class PublicSalonDetailsView(APIView):
    """
    Vue API pour obtenir les détails publics d'un salon
    """

    def get(self, request, salon_id=None):
        try:
            # Si salon_id est fourni, récupérer ce salon spécifique
            if salon_id:
                salon = TblSalon.objects.get(idTblSalon=salon_id)
                serializer = SalonDetailSerializer(salon)
                return Response(serializer.data)

            # Sinon, récupérer tous les salons
            else:
                salons = TblSalon.objects.all()
                serializer = SalonDetailSerializer(salons, many=True)
                return Response(serializer.data)

        except TblSalon.DoesNotExist:
            return Response(
                {"detail": "Salon non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
