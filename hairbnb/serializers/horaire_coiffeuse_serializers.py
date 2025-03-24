from rest_framework import serializers
from hairbnb.models import TblHoraireCoiffeuse, TblIndisponibilite


class HoraireCoiffeuseSerializer(serializers.ModelSerializer):
    jour_label = serializers.SerializerMethodField()

    class Meta:
        model = TblHoraireCoiffeuse
        fields = ['id', 'coiffeuse', 'jour', 'jour_label', 'heure_debut', 'heure_fin']

    def get_jour_label(self, obj):
        return obj.get_jour_display()


class IndisponibiliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblIndisponibilite
        fields = ['id', 'coiffeuse', 'date', 'heure_debut', 'heure_fin', 'motif']
