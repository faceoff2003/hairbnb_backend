from rest_framework import serializers
from hairbnb.models import TblPaiement
from hairbnb.serializers.rdvs_serializers import RendezVousSerializer


class PaiementSerializer(serializers.ModelSerializer):
    rendez_vous = RendezVousSerializer(source='rendez_vous', read_only=True)

    class Meta:
        model = TblPaiement
        fields = ['idPaiement', 'rendez_vous', 'montant_paye', 'date_paiement', 'methode', 'statut']
