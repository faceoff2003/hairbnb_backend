from rest_framework import serializers

from hairbnb.models import TblRendezVous, TblRendezVousService, TblPaiement
from hairbnb.serializers.salon_services_serializers import ServiceSerializer, SalonSerializer
from hairbnb.serializers.users_serializers import ClientSerializer, CoiffeuseSerializer


# 🔹 Serializer pour les services liés à un rendez-vous
class RendezVousServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()  # ✅ Remplace ServiceData par un Serializer DRF

    class Meta:
        model = TblRendezVousService
        fields = ['idRendezVousService', 'service', 'prix_applique', 'duree_estimee']


# 🔹 Serializer pour un rendez-vous
class RendezVousSerializer(serializers.ModelSerializer):
    client = ClientSerializer(source='client', read_only=True)
    coiffeuse = CoiffeuseSerializer(source='coiffeuse', read_only=True)
    salon = SalonSerializer(source='salon', read_only=True)  # ✅ Remplace SalonData
    services = RendezVousServiceSerializer(source='rendez_vous_services', many=True, read_only=True)

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous', 'client', 'coiffeuse', 'salon', 'date_heure',
            'statut', 'total_prix', 'duree_totale', 'services'
        ]


# 🔹 Serializer pour le paiement
class PaiementSerializer(serializers.ModelSerializer):
    rendez_vous = RendezVousSerializer(source='rendez_vous', read_only=True)

    class Meta:
        model = TblPaiement
        fields = ['idPaiement', 'rendez_vous', 'montant_paye', 'date_paiement', 'methode', 'statut']
