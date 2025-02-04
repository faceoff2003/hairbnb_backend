from hairbnb.models import TblPromotion
from rest_framework import serializers

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblPromotion
        fields = ['id', 'service', 'discount_percentage', 'start_date', 'end_date']