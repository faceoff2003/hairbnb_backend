from rest_framework import serializers

from hairbnb.models import TblCoiffeuse


class UpdateNomCommercialSerializer(serializers.ModelSerializer):
    nom_commercial = serializers.CharField(
        max_length=50,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Le nom commercial est requis',
            'blank': 'Le nom commercial ne peut pas être vide',
            'max_length': 'Le nom commercial ne peut pas dépasser 50 caractères'
        }
    )

    class Meta:
        model = TblCoiffeuse
        fields = ['nom_commercial']

    def validate_nom_commercial(self, value):
        """Validation personnalisée du nom commercial"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom commercial ne peut pas être vide")

        # Nettoyer la valeur (supprimer espaces en début/fin)
        return value.strip()

    def update(self, instance, validated_data):
        """Met à jour uniquement le nom commercial"""
        instance.nom_commercial = validated_data['nom_commercial']
        instance.save()
        return instance