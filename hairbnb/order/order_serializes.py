from rest_framework import serializers

from hairbnb.models import TblRendezVous, TblRendezVousService


class ServiceCommandeSerializer(serializers.ModelSerializer):
    """Serializer pour les services inclus dans une commande"""
    intitule_service = serializers.CharField(source='service.intitule_service')
    class Meta:
        model = TblRendezVousService
        fields = ['intitule_service', 'prix_applique', 'duree_estimee']

class CommandeSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes (rendez-vous payés)"""
    # Informations sur la coiffeuse
    nom_coiffeuse = serializers.CharField(source='coiffeuse.idTblUser.nom')
    prenom_coiffeuse = serializers.CharField(source='coiffeuse.idTblUser.prenom')
    # Informations sur le salon
    nom_salon = serializers.CharField(source='salon.nom_salon')

    # Informations sur le paiement - Adaptées à la relation inverse
    date_paiement = serializers.SerializerMethodField()
    montant_paye = serializers.SerializerMethodField()
    methode_paiement = serializers.SerializerMethodField()
    receipt_url = serializers.SerializerMethodField()

    # Détails des services
    services = ServiceCommandeSerializer(source='rendez_vous_services', many=True)

    def get_date_paiement(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.date_paiement if paiement else None

    def get_montant_paye(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.montant_paye if paiement else None

    def get_methode_paiement(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.methode.libelle if paiement and paiement.methode else None

    def get_receipt_url(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.receipt_url if paiement else None

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous',
            'date_heure',
            'statut',
            'nom_coiffeuse',
            'prenom_coiffeuse',
            'nom_salon',
            'total_prix',
            'duree_totale',
            'date_paiement',
            'montant_paye',
            'methode_paiement',
            'receipt_url',
            'services'
        ]




# from rest_framework import serializers
# from hairbnb.models import TblRendezVousService, TblRendezVous
#
#
# class ServiceCommandeSerializer(serializers.ModelSerializer):
#     """Serializer pour les services inclus dans une commande"""
#     intitule_service = serializers.CharField(source='service.intitule_service')
#
#     class Meta:
#         model = TblRendezVousService
#         fields = ['intitule_service', 'prix_applique', 'duree_estimee']
#
#
# class CommandeSerializer(serializers.ModelSerializer):
#     """Serializer pour les commandes (rendez-vous payés)"""
#     # Informations sur la coiffeuse
#     nom_coiffeuse = serializers.CharField(source='coiffeuse.idTblUser.nom')
#     prenom_coiffeuse = serializers.CharField(source='coiffeuse.idTblUser.prenom')
#
#     # Informations sur le salon
#     nom_salon = serializers.CharField(source='salon.nom_salon')
#
#     # Informations sur le paiement
#     date_paiement = serializers.DateTimeField(source='paiement.date_paiement')
#     montant_paye = serializers.DecimalField(source='paiement.montant_paye', max_digits=10, decimal_places=2)
#     methode_paiement = serializers.CharField(source='paiement.methode.libelle')
#     receipt_url = serializers.URLField(source='paiement.receipt_url')
#
#     # Détails des services
#     services = ServiceCommandeSerializer(source='rendez_vous_services', many=True)
#
#     class Meta:
#         model = TblRendezVous
#         fields = [
#             'idRendezVous',
#             'date_heure',
#             'statut',
#             'nom_coiffeuse',
#             'prenom_coiffeuse',
#             'nom_salon',
#             'total_prix',
#             'duree_totale',
#             'date_paiement',
#             'montant_paye',
#             'methode_paiement',
#             'receipt_url',
#             'services'
#         ]