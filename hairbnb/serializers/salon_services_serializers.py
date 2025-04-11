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


class SalonSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, source='salon_service.service')

    class Meta:
        model = TblSalon
        fields = ['idTblSalon', 'coiffeuse', 'services']


class TblSalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblSalon
        fields = ['idTblSalon', 'coiffeuse', 'nom_salon', 'slogan', 'logo_salon']


class TblSalonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblSalonImage
        fields = ['id', 'salon', 'image']


class TblAvisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblAvis
        fields = ['id', 'salon', 'client', 'note', 'commentaire', 'date']
        read_only_fields = ['date']