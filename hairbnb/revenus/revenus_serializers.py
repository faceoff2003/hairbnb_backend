# hairbnb/revenus/revenus_serializer.py

from rest_framework import serializers


class ClientSerializer(serializers.Serializer):
    """Serializer pour les informations du client"""
    nom = serializers.CharField(max_length=50)
    prenom = serializers.CharField(max_length=50)
    email = serializers.EmailField(allow_null=True, required=False)


class ServiceRdvSerializer(serializers.Serializer):
    """Serializer pour un service vendu dans un RDV"""
    nom = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=600, allow_blank=True)
    prix_ht = serializers.DecimalField(max_digits=10, decimal_places=2)
    prix_ttc = serializers.DecimalField(max_digits=10, decimal_places=2)
    duree_minutes = serializers.IntegerField(allow_null=True, required=False)


class DetailRdvSerializer(serializers.Serializer):
    """Serializer pour le détail d'un rendez-vous payé"""
    rdv_id = serializers.IntegerField()
    date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    client = ClientSerializer(allow_null=True, required=False)
    services = ServiceRdvSerializer(many=True)
    total_ht = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = serializers.DecimalField(max_digits=10, decimal_places=2)
    statut_rdv = serializers.CharField(max_length=20)
    salon = serializers.CharField(max_length=50, allow_null=True, required=False)


class ResumeRevenusSerializer(serializers.Serializer):
    """Serializer pour le résumé des revenus"""
    nb_rdv_payes = serializers.IntegerField()
    nb_clients_uniques = serializers.IntegerField()
    total_ht = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = serializers.DecimalField(max_digits=10, decimal_places=2)
    tva = serializers.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = serializers.DecimalField(max_digits=5, decimal_places=2)


class StatistiquesRevenusSerializer(serializers.Serializer):
    """Serializer pour les statistiques des revenus"""
    service_plus_vendu = serializers.CharField(max_length=100, allow_null=True, required=False)
    jour_le_plus_rentable = serializers.CharField(max_length=10, allow_null=True, required=False)
    revenus_par_jour = serializers.DictField(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    nb_services_differents = serializers.IntegerField()


class RevenusCoiffeuseSerializer(serializers.Serializer):
    """Serializer principal pour les revenus d'une coiffeuse"""
    success = serializers.BooleanField()
    periode = serializers.CharField(max_length=20)
    date_debut = serializers.DateField(format='%Y-%m-%d')
    date_fin = serializers.DateField(format='%Y-%m-%d')
    resume = ResumeRevenusSerializer()
    details_rdv = DetailRdvSerializer(many=True)
    statistiques = StatistiquesRevenusSerializer()


class RevenusErrorSerializer(serializers.Serializer):
    """Serializer pour les erreurs"""
    success = serializers.BooleanField()
    error = serializers.CharField(max_length=255)


class RevenusRequestSerializer(serializers.Serializer):
    """Serializer pour valider les paramètres de requête"""
    periode = serializers.ChoiceField(
        choices=['jour', 'semaine', 'mois', 'annee', 'custom'],
        default='mois'
    )
    date_debut = serializers.DateField(required=False, allow_null=True)
    date_fin = serializers.DateField(required=False, allow_null=True)
    salon_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Validation personnalisée pour les paramètres
        """
        periode = data.get('periode')
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')

        # Si période "custom", les dates sont obligatoires
        if periode == 'custom':
            if not date_debut or not date_fin:
                raise serializers.ValidationError(
                    "Les paramètres 'date_debut' et 'date_fin' sont obligatoires pour la période 'custom'"
                )

            # Vérifier que date_debut <= date_fin
            if date_debut > date_fin:
                raise serializers.ValidationError(
                    "La date de début doit être antérieure ou égale à la date de fin"
                )

        return data