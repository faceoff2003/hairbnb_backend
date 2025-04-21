import traceback

from rest_framework.decorators import parser_classes, api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.parsers import FormParser

from rest_framework.response import Response
from rest_framework import status
from hairbnb.models import TblSalonImage, TblSalon
from hairbnb.serializers.salon_services_serializers import TblSalonImageSerializer


class SalonImageListView(ListAPIView):
    serializer_class = TblSalonImageSerializer

    def get_queryset(self):
        salon_id = self.kwargs['salon_id']
        return TblSalonImage.objects.filter(salon__idTblSalon=salon_id)

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




# class SalonImageCreateView(CreateAPIView):
#     serializer_class = TblSalonImageSerializer
#     parser_classes = [MultiPartParser, FormParser]
#
#     def perform_create(self, serializer):
#         salon_id = self.kwargs.get('salon_id')
#         print("➡️ ID salon reçu :", salon_id)
#         print("📁 Fichiers reçus :", self.request.FILES)
#
#         try:
#             salon = TblSalon.objects.get(idTblSalon=salon_id)
#         except TblSalon.DoesNotExist:
#             raise NotFound(detail="Salon introuvable")
#
#         if 'image' not in self.request.FILES:
#             raise DRFValidationError({"image": "Aucune image fournie dans la requête"})
#
#         try:
#             serializer.save(salon=salon)
#         except DjangoValidationError as e:
#             raise DRFValidationError({"image": e.messages[0]})
#
#     def create(self, request, *args, **kwargs):
#         try:
#             return super().create(request, *args, **kwargs)
#         except DRFValidationError as ve:
#             return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             print("🛑 Exception inattendue lors de l'ajout d'image :")
#             traceback.print_exc()
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SalonImageDeleteView(DestroyAPIView):
    queryset = TblSalonImage.objects.all()
    serializer_class = TblSalonImageSerializer
    lookup_field = 'id'