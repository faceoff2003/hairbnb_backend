# Fichier: serializers.py (à créer ou compléter)

from rest_framework import serializers

from hairbnb.models import TblEmailType, TblEmailStatus, TblUser, TblSalon, TblRendezVous, TblEmailNotification


class EmailTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblEmailType
        fields = ['idTblEmailType', 'code', 'libelle']

class EmailStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblEmailStatus
        fields = ['idTblEmailStatus', 'code', 'libelle']

class UserMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour TblUser, utilisé dans les relations."""
    class Meta:
        model = TblUser
        fields = ['idTblUser', 'nom', 'prenom', 'email']

class SalonMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour TblSalon, utilisé dans les relations."""
    class Meta:
        model = TblSalon
        fields = ['idTblSalon', 'nom_salon']

class RendezVousMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour TblRendezVous, utilisé dans les relations."""
    class Meta:
        model = TblRendezVous
        fields = ['idRendezVous', 'date_heure', 'statut']

class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer complet pour TblEmailNotification."""
    destinataire = UserMinimalSerializer(read_only=True)
    salon = SalonMinimalSerializer(read_only=True)
    rendez_vous = RendezVousMinimalSerializer(read_only=True)
    type_email = EmailTypeSerializer(read_only=True)
    statut = EmailStatusSerializer(read_only=True)

    class Meta:
        model = TblEmailNotification
        fields = [
            'idTblEmailNotification', 'destinataire', 'salon', 'rendez_vous',
            'type_email', 'statut', 'sujet', 'contenu', 'date_creation',
            'date_envoi', 'tentatives', 'email_id'
        ]

class EmailNotificationCreateSerializer(serializers.Serializer):
    """
    Serializer pour la création d'une notification email via l'API.
    C'est un serializer non basé sur un modèle pour permettre plus de flexibilité.
    """
    toEmail = serializers.EmailField(required=True)
    toName = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    templateId = serializers.CharField(required=True)
    templateData = serializers.JSONField(required=False, default=dict)
    rendezVousId = serializers.IntegerField(required=False, allow_null=True)

    def validate_templateId(self, value):
        """Vérifie que le template ID existe dans la base de données."""
        try:
            TblEmailType.objects.get(code=value)
            return value
        except TblEmailType.DoesNotExist:
            raise serializers.ValidationError(f"Le template ID '{value}' n'existe pas")

    def validate_rendezVousId(self, value):
        """Vérifie que le rendez-vous existe si un ID est fourni."""
        if value is not None:
            try:
                TblRendezVous.objects.get(idRendezVous=value)
                return value
            except TblRendezVous.DoesNotExist:
                raise serializers.ValidationError(f"Le rendez-vous avec ID {value} n'existe pas")
        return value