from hairbnb.currentUser.currentUser_business_logic import CurrentUserData
from hairbnb.models import TblPromotion
from django.utils.timezone import now
from decimal import Decimal


class CartItemData:
    def __init__(self, cart_item):
        self.id = cart_item.idTblCartItem
        self.service = self._get_service_data(cart_item.service)
        self.quantity = cart_item.quantity

    def _get_service_data(self, service):
        """ Récupère les informations du service et applique la promotion si disponible """
        prix_standard = service.service_prix.first().prix.prix if service.service_prix.exists() else Decimal("0.00")

        # Vérifier s'il y a une promotion active
        promo = TblPromotion.objects.filter(
            service=service,
            start_date__lte=now(),
            end_date__gte=now()
        ).first()

        if promo:  # Appliquer la réduction
            reduction = (promo.discount_percentage / Decimal("100")) * prix_standard
            prix_final = prix_standard - reduction
            promo_data = {
                "idPromotion": promo.idPromotion,
                "service_id": service.idTblService,
                "discount_percentage": promo.discount_percentage,
                "start_date": promo.start_date,
                "end_date": promo.end_date,
                "is_active": promo.is_active()
            }
        else:  # Pas de promo
            prix_final = prix_standard
            promo_data = None

        return {
            "idTblService": service.idTblService,
            "intitule_service": service.intitule_service,
            "description": service.description,
            "temps_minutes": service.service_temps.first().temps.minutes if service.service_temps.exists() else 0,
            "prix": float(prix_standard),
            "promotion": promo_data,
            "prix_final": float(prix_final)  # ✅ Prix recalculé avec promo appliquée
        }

    def to_dict(self):
        return self.__dict__



class CartData:
    def __init__(self, cart):
        self.idTblCart = cart.idTblCart
        self.user = CurrentUserData(cart.user).to_dict()  # Réutilise CurrentUserData
        self.items = [CartItemData(item).to_dict() for item in cart.items.all()]
        self.total_price = cart.total_price()  # Méthode qui calcule le total

    def to_dict(self):
        return self.__dict__