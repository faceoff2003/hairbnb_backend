# serializers.py
from rest_framework import serializers
from hairbnb.models import TblService, TblSalonService, TblServicePrix, TblServiceTemps, TblPrix, TblTemps


class ServiceCreateSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    intitule_service = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    prix = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    temps_minutes = serializers.IntegerField(required=True)

    class Meta:
        fields = ['userId', 'intitule_service', 'description', 'prix', 'temps_minutes']


class ServiceResponseSerializer(serializers.ModelSerializer):
    prix = serializers.SerializerMethodField()
    temps_minutes = serializers.SerializerMethodField()

    class Meta:
        model = TblService
        fields = ['idTblService', 'intitule_service', 'description', 'prix', 'temps_minutes']

    def get_prix(self, obj):
        service_prix = obj.service_prix.first()
        return service_prix.prix.prix if service_prix else 0.0

    def get_temps_minutes(self, obj):
        service_temps = obj.service_temps.first()
        return service_temps.temps.minutes if service_temps else 0
