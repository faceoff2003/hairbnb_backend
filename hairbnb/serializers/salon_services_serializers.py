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