from rest_framework import serializers
from hairbnb.models import TblService, TblTemps, TblPrix, TblSalonService, TblSalon, TblSalonImage, TblAvis


class TempsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblTemps
        fields = ['idTblTemps', 'minutes']


class PrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblPrix
        fields = ['idTblPrix', 'prix']


class ServiceSerializer(serializers.ModelSerializer):
    temps = TempsSerializer(source="service_temps.temps", read_only=True)
    prix = PrixSerializer(source="service_prix.prix", read_only=True)

    class Meta:
        model = TblService
        fields = ['idTblService', 'intitule_service', 'description', 'temps', 'prix']

#
# class SalonSerializer(serializers.ModelSerializer):
#     services = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'services', 'nom_salon', 'slogan', 'a_propos', 'logo_salon', 'position',
#                   'adresse']
#
#     def get_services(self, obj):
#         # Récupérer les services via la table de liaison
#         salon_services = TblSalonService.objects.filter(salon=obj)
#         services = [ss.service for ss in salon_services]
#         return ServiceSerializer(services, many=True).data
#
#
# class TblSalonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'logo_salon', 'position', 'adresse']
#
#
# class TblSalonImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalonImage
#         fields = ['id', 'salon', 'image']
#
#
# class TblAvisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblAvis
#         fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
#         read_only_fields = ['date']





# from rest_framework import serializers
# from hairbnb.models import TblService, TblTemps, TblPrix,TblSalon, TblSalonImage, TblAvis
#
#
# class TempsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblTemps
#         fields = ['idTblTemps', 'minutes']
#
#
# class PrixSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblPrix
#         fields = ['idTblPrix', 'prix']
#
#
# class ServiceSerializer(serializers.ModelSerializer):
#     temps = TempsSerializer(source="service_temps.temps", read_only=True)
#     prix = PrixSerializer(source="service_prix.prix", read_only=True)
#
#     class Meta:
#         model = TblService
#         fields = ['idTblService', 'intitule_service', 'description', 'temps', 'prix']
#
#
# class SalonSerializer(serializers.ModelSerializer):
#     services = ServiceSerializer(many=True, source='salon_service.service')
#
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'services']
#
#
# class TblSalonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalon
#         fields = ['idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'logo_salon']
#
#
# class TblSalonImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblSalonImage
#         fields = ['id', 'salon', 'image']
#
#
# class TblAvisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblAvis
#         fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
#         read_only_fields = ['date']