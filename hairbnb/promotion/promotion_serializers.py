from rest_framework import serializers
from django.utils.timezone import make_aware
from datetime import datetime
from hairbnb.models import TblPromotion


class PromotionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la modification d'une promotion existante.
    """

    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0.01,
        max_value=100.00,
        error_messages={
            'min_value': 'Le pourcentage doit être supérieur à 0%',
            'max_value': 'Le pourcentage ne peut pas dépasser 100%',
            'required': 'Le pourcentage de réduction est obligatoire'
        }
    )

    start_date = serializers.CharField(help_text="Format: YYYY-MM-DD")
    end_date = serializers.CharField(help_text="Format: YYYY-MM-DD")

    class Meta:
        model = TblPromotion
        fields = ['discount_percentage', 'start_date', 'end_date']

    def validate_start_date(self, value):
        """Valider et convertir la date de début"""
        try:
            parsed_date = datetime.strptime(value.split("T")[0], "%Y-%m-%d")
            return make_aware(parsed_date)
        except ValueError:
            raise serializers.ValidationError("Format de date invalide. Utilisez YYYY-MM-DD")

    def validate_end_date(self, value):
        """Valider et convertir la date de fin"""
        try:
            parsed_date = datetime.strptime(value.split("T")[0], "%Y-%m-%d")
            return make_aware(parsed_date)
        except ValueError:
            raise serializers.ValidationError("Format de date invalide. Utilisez YYYY-MM-DD")

    def validate(self, data):
        """Validation globale des données"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'La date de fin doit être postérieure à la date de début'
            })

        return data