from django.utils.timezone import now
from django.core.paginator import Paginator

class PromotionManager:
    def __init__(self, service):
        self.service = service
        self.now = now()

        # Préchargement de toutes les promotions, triées par date de début
        self.promos = list(service.promotions.all().order_by('-start_date'))

        # Séparation par catégorie
        self.active = []
        self.upcoming = []
        self.expired = []

        for promo in self.promos:
            if promo.start_date <= self.now <= promo.end_date:
                self.active.append(promo)
            elif promo.start_date > self.now:
                self.upcoming.append(promo)
            else:
                self.expired.append(promo)

        # Comptages
        self.count_upcoming = len(self.upcoming)
        self.count_expired = len(self.expired)

    def serialize(self, promo, status):
        return {
            "idPromotion": promo.idPromotion,
            "service_id": promo.service.idTblService,
            "discount_percentage": float(promo.discount_percentage),
            "start_date": promo.start_date.isoformat(),
            "end_date": promo.end_date.isoformat(),
            "status": status
        }

    def get_active(self):
        if self.active:
            return self.serialize(self.active[0], "active")
        return None

    def get_upcoming(self, limit=4):
        return [self.serialize(p, "upcoming") for p in self.upcoming[:limit]]

    def get_expired(self, page=1, page_size=5):
        paginator = Paginator(self.expired, page_size)
        page_obj = paginator.get_page(page)
        return {
            "results": [self.serialize(p, "expired") for p in page_obj],
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }

    def get_counts(self):
        return {
            "upcoming": self.count_upcoming,
            "expired": self.count_expired,
            "active": 1 if self.active else 0,
        }
