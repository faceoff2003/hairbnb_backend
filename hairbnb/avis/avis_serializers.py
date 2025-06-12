# serializers.py - Système d'avis

from rest_framework import serializers
from django.utils import timezone
from hairbnb.models import (
    TblAvis, TblAvisStatut, TblRendezVous, TblClient,
    TblSalon
)


# 1️⃣ SERIALIZER POUR LES STATUTS D'AVIS
class AvisStatutSerializer(serializers.ModelSerializer):
    """Serializer pour les statuts d'avis"""

    class Meta:
        model = TblAvisStatut
        fields = ['idTblAvisStatut', 'code', 'libelle', 'description']


# 2️⃣ SERIALIZERS LÉGERS POUR LES RELATIONS
class ClientAvisSerializer(serializers.ModelSerializer):
    """Serializer léger pour les infos client dans les avis"""
    nom = serializers.CharField(source='idTblUser.nom', read_only=True)
    prenom = serializers.CharField(source='idTblUser.prenom', read_only=True)
    photo_profil = serializers.CharField(source='idTblUser.photo_profil', read_only=True)

    class Meta:
        model = TblClient
        fields = ['nom', 'prenom', 'photo_profil']


class SalonAvisSerializer(serializers.ModelSerializer):
    """Serializer léger pour les infos salon dans les avis"""

    class Meta:
        model = TblSalon
        fields = ['idTblSalon', 'nom_salon', 'logo_salon']


class RendezVousAvisSerializer(serializers.ModelSerializer):
    """Serializer léger pour les infos RDV dans les avis"""

    class Meta:
        model = TblRendezVous
        fields = ['idRendezVous', 'date_heure', 'total_prix', 'duree_totale']


# 3️⃣ SERIALIZER POUR CRÉER UN AVIS (avec auth Firebase)
class AvisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un nouvel avis - Avec authentification Firebase"""

    # Le client sera automatiquement récupéré depuis request.user
    # Le salon et RDV seront récupérés depuis le RDV sélectionné
    idRendezVous = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = TblAvis
        fields = ['idRendezVous', 'note', 'commentaire']
        extra_kwargs = {
            'note': {'required': True},
            'commentaire': {'required': True, 'min_length': 10, 'max_length': 1000},
        }

    def validate_note(self, value):
        """Valider que la note est entre 1 et 5"""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5.")
        return value

    def validate_commentaire(self, value):
        """Valider la longueur du commentaire"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le commentaire doit contenir au moins 10 caractères.")
        if len(value.strip()) > 1000:
            raise serializers.ValidationError("Le commentaire ne peut pas dépasser 1000 caractères.")
        return value.strip()

    def validate_idRendezVous(self, value):
        """Valider que le RDV existe et appartient au client connecté"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Utilisateur non authentifié.")

        try:
            # Récupérer le client depuis l'utilisateur Firebase connecté
            client = TblClient.objects.get(idTblUser__uuid=request.user.uuid)

            # Vérifier que le RDV existe et appartient à ce client
            rdv = TblRendezVous.objects.get(
                idRendezVous=value,
                client=client
            )

            # Vérifier que le RDV est terminé
            if rdv.statut != 'terminé':
                raise serializers.ValidationError("Seuls les rendez-vous terminés peuvent recevoir un avis.")

            # Vérifier qu'aucun avis n'existe déjà pour ce RDV
            if TblAvis.objects.filter(rendez_vous=rdv).exists():
                raise serializers.ValidationError("Un avis a déjà été donné pour ce rendez-vous.")

            return value

        except TblClient.DoesNotExist:
            raise serializers.ValidationError("Client non trouvé.")
        except TblRendezVous.DoesNotExist:
            raise serializers.ValidationError("Rendez-vous non trouvé ou non autorisé.")

    def create(self, validated_data):
        """Créer l'avis avec les relations automatiques"""
        request = self.context.get('request')
        idRendezVous = validated_data.pop('idRendezVous')

        # Récupérer le client depuis l'utilisateur connecté
        client = TblClient.objects.get(idTblUser__uuid=request.user.uuid)

        # Récupérer le RDV
        rdv = TblRendezVous.objects.get(idRendezVous=idRendezVous)

        # Récupérer le statut "visible" par défaut
        statut_visible = TblAvisStatut.objects.get(code='visible')

        # Créer l'avis
        avis = TblAvis.objects.create(
            rendez_vous=rdv,
            client=client,
            salon=rdv.salon,
            statut=statut_visible,
            **validated_data
        )

        return avis


# 4️⃣ SERIALIZER POUR AFFICHER UN AVIS COMPLET
class AvisDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour afficher un avis"""
    client = ClientAvisSerializer(read_only=True)
    salon = SalonAvisSerializer(read_only=True)
    rendez_vous = RendezVousAvisSerializer(read_only=True)
    statut = AvisStatutSerializer(read_only=True)
    date_formatted = serializers.SerializerMethodField()
    client_nom_complet = serializers.CharField(read_only=True)

    class Meta:
        model = TblAvis
        fields = [
            'id', 'note', 'commentaire', 'date', 'date_formatted',
            'client', 'salon', 'rendez_vous', 'statut', 'client_nom_complet'
        ]

    def get_date_formatted(self, obj):
        """Formater la date d'avis"""
        return obj.date.strftime('%d/%m/%Y à %H:%M')


# 5️⃣ SERIALIZER POUR LISTER LES AVIS (version allégée)
class AvisListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les avis - Version publique allégée"""
    client_nom = serializers.CharField(source='client.idTblUser.prenom', read_only=True)
    client_photo = serializers.CharField(source='client.idTblUser.photo_profil', read_only=True)
    date_formatted = serializers.SerializerMethodField()

    class Meta:
        model = TblAvis
        fields = [
            'id', 'note', 'commentaire', 'date_formatted',
            'client_nom', 'client_photo'
        ]

    def get_date_formatted(self, obj):
        return obj.date.strftime('%d/%m/%Y')


# 6️⃣ SERIALIZER POUR LES RDV ÉLIGIBLES AUX AVIS
class RdvEligibleAvisSerializer(serializers.ModelSerializer):
    """Serializer pour les RDV éligibles aux avis d'un client"""
    salon_nom = serializers.CharField(source='salon.nom_salon', read_only=True)
    salon_logo = serializers.CharField(source='salon.logo_salon', read_only=True)
    date_formatted = serializers.SerializerMethodField()
    services_noms = serializers.SerializerMethodField()
    est_eligible = serializers.SerializerMethodField()

    class Meta:
        model = TblRendezVous
        fields = [
            'idRendezVous', 'date_heure', 'date_formatted', 'total_prix',
            'duree_totale', 'salon_nom', 'salon_logo', 'services_noms', 'est_eligible'
        ]

    def get_date_formatted(self, obj):
        return obj.date_heure.strftime('%d/%m/%Y à %H:%M')

    def get_services_noms(self, obj):
        """Récupérer les noms des services du RDV"""
        return [
            service.service.intitule_service
            for service in obj.rendez_vous_services.all()
        ]

    def get_est_eligible(self, obj):
        """Vérifier si le RDV est éligible aux avis"""
        from datetime import timedelta

        # RDV terminé + 2h passées + pas d'avis existant
        if obj.statut != 'terminé':
            return False

        fin_theorique = obj.date_heure + timedelta(minutes=obj.duree_totale or 60)
        maintenant = timezone.now()

        if maintenant < fin_theorique + timedelta(hours=2):
            return False

        return not obj.avis.exists()


# 7️⃣ SERIALIZER POUR LES STATISTIQUES D'AVIS
class AvisStatistiquesSerializer(serializers.Serializer):
    """Serializer pour les statistiques d'avis d'un salon"""
    moyenne_notes = serializers.FloatField()
    total_avis = serializers.IntegerField()
    repartition_notes = serializers.DictField()
    avis_recents = AvisListSerializer(many=True)

    # Répartition par note
    note_5 = serializers.IntegerField()
    note_4 = serializers.IntegerField()
    note_3 = serializers.IntegerField()
    note_2 = serializers.IntegerField()
    note_1 = serializers.IntegerField()


# 8️⃣ SERIALIZER POUR MES AVIS (historique client)
class MesAvisSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des avis d'un client"""
    salon_nom = serializers.CharField(source='salon.nom_salon', read_only=True)
    salon_logo = serializers.CharField(source='salon.logo_salon', read_only=True)
    rdv_date = serializers.CharField(source='rendez_vous.date_heure', read_only=True)
    date_formatted = serializers.SerializerMethodField()
    statut_libelle = serializers.CharField(source='statut.libelle', read_only=True)

    class Meta:
        model = TblAvis
        fields = [
            'id', 'note', 'commentaire', 'date', 'date_formatted',
            'salon_nom', 'salon_logo', 'rdv_date', 'statut_libelle'
        ]

    def get_date_formatted(self, obj):
        return obj.date.strftime('%d/%m/%Y à %H:%M')