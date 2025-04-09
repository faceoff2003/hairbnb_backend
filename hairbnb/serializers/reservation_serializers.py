# serializers/reservation_serializer.py

from rest_framework import serializers
from hairbnb.models import TblRendezVous, TblRendezVousService

class RendezVousServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblRendezVousService
        fields = ['service', 'prix_applique', 'duree_estimee']

class ReservationSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.idTblUser.nom', read_only=True)
    client_prenom = serializers.CharField(source='client.idTblUser.prenom', read_only=True)
    services = RendezVousServiceSerializer(source='rendez_vous_services', many=True)

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous',
            'client_nom',
            'client_prenom',
            'date_heure',
            'statut',
            'total_prix',
            'duree_totale',
            'services'
        ]
