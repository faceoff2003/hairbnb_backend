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


class CommandeCoiffeuseSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes (rendez-vous) vues par les coiffeuses"""
    # Informations sur le client
    nom_client = serializers.CharField(source='client.idTblUser.nom')
    prenom_client = serializers.CharField(source='client.idTblUser.prenom')
    telephone_client = serializers.CharField(source='client.idTblUser.numero_telephone')
    email_client = serializers.CharField(source='client.idTblUser.email')

    # Informations sur le salon
    nom_salon = serializers.CharField(source='salon.nom_salon')

    # Informations sur le paiement
    date_paiement = serializers.SerializerMethodField()
    montant_paye = serializers.SerializerMethodField()
    statut_paiement = serializers.SerializerMethodField()

    # Détails des services
    services = ServiceCommandeSerializer(source='rendez_vous_services', many=True)

    def get_date_paiement(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.date_paiement if paiement else None

    def get_montant_paye(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.montant_paye if paiement else None

    def get_statut_paiement(self, obj):
        paiement = obj.tblpaiement_set.first()
        return paiement.statut.libelle if paiement and paiement.statut else "Non payé"

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous',
            'date_heure',
            'statut',
            'nom_client',
            'prenom_client',
            'telephone_client',
            'email_client',
            'nom_salon',
            'total_prix',
            'duree_totale',
            'statut_paiement',
            'date_paiement',
            'montant_paye',
            'services',
            'est_archive'
        ]


class UpdateRendezVousSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour le statut et la date/heure d'un rendez-vous"""

    class Meta:
        model = TblRendezVous
        fields = ['statut', 'date_heure']

    def validate_statut(self, value):
        # Vérifier que le statut est valide
        valid_statuses = ['en attente', 'confirmé', 'annulé', 'terminé']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Le statut doit être l'un des suivants: {', '.join(valid_statuses)}")
        return value

    def validate_date_heure(self, value):
        # Vérifier que la date n'est pas dans le passé
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("La date et l'heure ne peuvent pas être dans le passé")
        return value