from rest_framework import serializers
from hairbnb.models import TblCart, TblCartItem

class CartItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.intitule_service', read_only=True)
    service_price = serializers.SerializerMethodField()

    class Meta:
        model = TblCartItem
        fields = ['idTblCartItem', 'cart', 'service', 'service_name', 'service_price', 'quantity']

    def get_service_price(self, obj):
        """ Récupère le prix du service via la relation `TblServicePrix` """
        try:
            return obj.service.service_prix.first().prix.prix
        except AttributeError:
            return None

class CartSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.nom', read_only=True)
    total_price = serializers.SerializerMethodField()
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = TblCart
        fields = ['idTblCart', 'user', 'user_name', 'created_at', 'total_price', 'items']

    def get_total_price(self, obj):
        """ Calcule le prix total du panier """
        return obj.total_price()
