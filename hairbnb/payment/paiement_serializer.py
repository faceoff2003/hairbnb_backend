from rest_framework import serializers
from hairbnb.models import TblPaiement, TblPaiementStatut, TblMethodePaiement


class PaiementStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblPaiementStatut
        fields = ['idTblPaiementStatut', 'code', 'libelle']


class MethodePaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblMethodePaiement
        fields = ['idTblMethodePaiement', 'code', 'libelle']


class PaiementSerializer(serializers.ModelSerializer):
    statut = PaiementStatutSerializer(read_only=True)
    methode = MethodePaiementSerializer(read_only=True)

    class Meta:
        model = TblPaiement
        fields = [
            'idTblPaiement',
            'rendez_vous',
            'utilisateur',
            'montant_paye',
            'date_paiement',
            'statut',
            'methode',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'stripe_customer_id',
            'stripe_checkout_session_id',
            'email_client',
            'receipt_url'
        ]


from rest_framework import serializers
from hairbnb.models import TblPaiement, TblPaiementStatut, TblMethodePaiement, TblRendezVous, TblUser


class PaiementCreateSerializer(serializers.ModelSerializer):
    rendez_vous_id = serializers.IntegerField(write_only=True)
    utilisateur_id = serializers.IntegerField(write_only=True)
    statut_code = serializers.CharField(write_only=True)
    methode_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = TblPaiement
        fields = [
            'rendez_vous_id',
            'utilisateur_id',
            'montant_paye',
            'statut_code',
            'methode_code',
            'stripe_payment_intent_id',
            'stripe_checkout_session_id',
            'email_client'
        ]

    def create(self, validated_data):
        # Récupération des objets liés
        rendez_vous = TblRendezVous.objects.get(idRendezVous=validated_data.pop('rendez_vous_id'))
        utilisateur = TblUser.objects.get(idTblUser=validated_data.pop('utilisateur_id'))
        statut = TblPaiementStatut.objects.get(code=validated_data.pop('statut_code'))
        methode = None

        if 'methode_code' in validated_data:
            try:
                methode = TblMethodePaiement.objects.get(code=validated_data.pop('methode_code'))
            except TblMethodePaiement.DoesNotExist:
                raise serializers.ValidationError("Méthode de paiement invalide")

        return TblPaiement.objects.create(
            rendez_vous=rendez_vous,
            utilisateur=utilisateur,
            statut=statut,
            methode=methode,
            **validated_data
        )


from rest_framework import serializers
from hairbnb.models import TblPaiement, TblPaiementStatut, TblMethodePaiement, TblRendezVous, TblUser


class PaiementStatutNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblPaiementStatut
        fields = ['code', 'libelle']


class MethodePaiementNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblMethodePaiement
        fields = ['code', 'libelle']


class PaiementDetailSerializer(serializers.ModelSerializer):
    statut = PaiementStatutNestedSerializer(read_only=True)
    methode = MethodePaiementNestedSerializer(read_only=True)
    utilisateur = serializers.StringRelatedField(read_only=True)
    rendez_vous_id = serializers.IntegerField(source='rendez_vous.idRendezVous', read_only=True)

    class Meta:
        model = TblPaiement
        fields = [
            'idTblPaiement',
            'rendez_vous_id',
            'utilisateur',
            'montant_paye',
            'date_paiement',
            'statut',
            'methode',
            'stripe_payment_intent_id',
            'stripe_checkout_session_id',
            'email_client',
            'receipt_url'
        ]


class RefundSerializer(serializers.Serializer):
    id_paiement = serializers.IntegerField(required=True)
    montant = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        help_text="Montant à rembourser (laisser vide pour remboursement total)"
    )


