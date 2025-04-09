from rest_framework import serializers

from hairbnb.models import TblRendezVous


class ReservationLightSerializer(serializers.ModelSerializer):
    #idRendezVous = serializers.IntegerField()
    client_nom = serializers.CharField(source='client.idTblUser.nom')
    client_prenom = serializers.CharField(source='client.idTblUser.prenom')
    client_photo = serializers.ImageField(source='client.idTblUser.photo_profil', allow_null=True)
    date_heure = serializers.DateTimeField()
    statut = serializers.CharField()
    total_prix = serializers.FloatField()
    duree_totale = serializers.IntegerField()

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous',
            'client_nom',
            'client_prenom',
            'client_photo',
            'date_heure',
            'statut',
            'total_prix',
            'duree_totale',
        ]
