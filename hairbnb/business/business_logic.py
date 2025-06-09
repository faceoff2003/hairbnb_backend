from datetime import datetime, timedelta
import stripe
from hairbnb.models import TblRendezVous, TblHoraireCoiffeuse, TblIndisponibilite
from hairbnb.salon.salon_business_logic import SalonData
from hairbnb.salon_services.salon_services_business_logic import ServiceData
from hairbnb_backend import settings_test

# class CoiffeuseData:
class CoiffeuseData:
    def __init__(self, coiffeuse):
        self.idTblCoiffeuse = coiffeuse.pk  # 🔥 Clé primaire
        self.idTblUser = coiffeuse.idTblUser.idTblUser
        self.denomination_sociale = coiffeuse.denomination_sociale
        self.tva = coiffeuse.tva
        self.position = coiffeuse.position

        # Infos utilisateur
        user = coiffeuse.idTblUser
        self.uuid = user.uuid
        self.nom = user.nom
        self.prenom = user.prenom
        self.email = user.email
        self.numero_telephone = user.numero_telephone
        self.date_naissance = user.date_naissance
        self.sexe = user.sexe
        self.is_active = user.is_active
        self.photo_profil = user.photo_profil.url if user.photo_profil else None

        # Adresse
        adresse = user.adresse
        if adresse:
            self.numero = adresse.numero
            self.boite_postale = adresse.boite_postale
            self.nom_rue = adresse.rue.nom_rue
            self.commune = adresse.rue.localite.commune
            self.code_postal = adresse.rue.localite.code_postal
        else:
            self.numero = None
            self.boite_postale = None
            self.nom_rue = None
            self.commune = None
            self.code_postal = None

    def to_dict(self):
        return self.__dict__


# class SalonData:
#     def __init__(self, salon, filtered_services=None):
#         self.idTblSalon = salon.idTblSalon
#
#         # Gestion de la relation avec la coiffeuse (adaptation au nouveau modèle)
#         # Vérifier si le salon a toujours une coiffeuse propriétaire principale
#         if hasattr(salon, 'coiffeuse') and salon.coiffeuse:
#             self.coiffeuse_id = salon.coiffeuse.idTblUser.idTblUser
#         else:
#             # Sinon, essayer de trouver la coiffeuse propriétaire via TblCoiffeuseSalon
#             from hairbnb.models import TblCoiffeuseSalon
#             proprietaire = TblCoiffeuseSalon.objects.filter(salon=salon, est_proprietaire=True).first()
#             if proprietaire:
#                 self.coiffeuse_id = proprietaire.coiffeuse.idTblUser.idTblUser
#             else:
#                 # Fallback si aucune coiffeuse propriétaire n'est trouvée
#                 self.coiffeuse_id = None
#
#         # ✅ Soit on utilise les services filtrés (pagination), soit tous
#         services_source = filtered_services if filtered_services is not None else salon.salon_service.all().order_by(
#             'service__intitule_service')
#         self.services = [ServiceData(service.service).to_dict() for service in services_source]
#
#     def to_dict(self):
#         return self.__dict__

class FullSalonServiceData:
    def __init__(self, salon_service):
        # Informations sur le service
        self.idTblService = salon_service.service.idTblService
        self.intitule_service = salon_service.service.intitule_service
        self.description = salon_service.service.description

        # Temps et prix liés au service (via la table de jonction)
        service_temps = salon_service.service.service_temps.first()
        self.temps_minutes = service_temps.temps.minutes if service_temps else None

        service_prix = salon_service.service.service_prix.first()
        self.prix = service_prix.prix.prix if service_prix else None

        # Informations sur le salon et la coiffeuse
        self.idTblSalon = salon_service.salon.idTblSalon
        self.coiffeuse_id = salon_service.salon.coiffeuse.idTblUser.idTblUser

    def to_dict(self):
        return self.__dict__


class ClientData:
    def __init__(self, client):
        self.idTblUser = client.idTblUser.idTblUser  # ID lié à l'utilisateur

        # Infos utilisateur
        user = client.idTblUser
        self.uuid = user.uuid
        self.nom = user.nom
        self.prenom = user.prenom
        self.email = user.email
        self.numero_telephone = user.numero_telephone
        self.date_naissance = user.date_naissance
        self.sexe = user.sexe
        self.is_active = user.is_active
        self.photo_profil = user.photo_profil.url if user.photo_profil else None

        # Adresse
        adresse = user.adresse
        if adresse:
            self.numero = adresse.numero
            self.boite_postale = adresse.boite_postale
            self.nom_rue = adresse.rue.nom_rue
            self.commune = adresse.rue.localite.commune
            self.code_postal = adresse.rue.localite.code_postal
        else:
            self.numero = None
            self.boite_postale = None
            self.nom_rue = None
            self.commune = None
            self.code_postal = None

    def to_dict(self):
        return self.__dict__

# class MinimalCoiffeuseData:
#     def __init__(self, coiffeuse):
#         user = coiffeuse.idTblUser  # Récupération de l'utilisateur associé à la coiffeuse
#         self.idTblUser = user.idTblUser
#         self.uuid = user.uuid
#         self.nom = user.nom
#         self.prenom = user.prenom
#         self.photo_profil = user.photo_profil.url if user.photo_profil else None  # Vérification de la photo
#         self.position = coiffeuse.position
#
#     def to_dict(self):
#         return self.__dict__


from django.utils.timezone import now

# # class ServiceData:
# class ServiceData:
#     def __init__(self, service):
#         self.idTblService = service.idTblService
#         self.intitule_service = service.intitule_service
#         self.description = service.description
#
#         # ✅ NOUVEAU : Ajout de la catégorie
#         self.category_id = service.categorie.idTblCategorie if service.categorie else None
#
#         # Récupération du temps
#         service_temps = service.service_temps.first()
#         self.temps_minutes = service_temps.temps.minutes if service_temps else None
#         # Récupération du prix
#         service_prix = service.service_prix.first()
#         self.prix = service_prix.prix.prix if service_prix else None
#         # Variables pour stocker les promotions
#         self.promotion_active = None
#         self.promotions_a_venir = []
#         self.promotions_expirees = []
#         self.prix_final = self.prix
#         # Récupère toutes les promotions pour le service
#         now_date = now()
#         # 1. Récupérer la promotion active
#         active_promo = service.promotions.filter(
#             start_date__lte=now_date,
#             end_date__gte=now_date
#         ).first()
#         if active_promo:
#             self.promotion_active = self._format_promotion(active_promo)
#             # Calcul du prix final avec la réduction active
#             self.prix_final = self.prix * (1 - (active_promo.discount_percentage / 100))
#         # 2. Récupérer les promotions à venir (max toutes)
#         future_promos = service.promotions.filter(
#             start_date__gt=now_date
#         ).order_by('start_date')
#         for promo in future_promos:
#             self.promotions_a_venir.append(self._format_promotion(promo))
#         # 3. Récupérer les promotions expirées
#         # Calculer combien on peut encore prendre pour atteindre le total de 10
#         remaining_slots = 10 - (1 if active_promo else 0) - len(self.promotions_a_venir)
#         if remaining_slots > 0:
#             expired_promos = service.promotions.filter(
#                 end_date__lt=now_date
#             ).order_by('-end_date')[:remaining_slots]  # Trier par date de fin décroissante (récentes d'abord)
#             for promo in expired_promos:
#                 self.promotions_expirees.append(self._format_promotion(promo))
#
#     def _format_promotion(self, promo):
#         """Formate une promotion en dictionnaire"""
#         now_date = now()
#         status = "active" if promo.start_date <= now_date <= promo.end_date else (
#             "future" if promo.start_date > now_date else "expired"
#         )
#         return {
#             "idPromotion": promo.idPromotion,
#             "service_id": promo.service.idTblService,
#             "discount_percentage": promo.discount_percentage,
#             "start_date": promo.start_date.isoformat(),
#             "end_date": promo.end_date.isoformat(),
#             "status": status
#         }
#
#     def to_dict(self):
#         return self.__dict__


class PromotionData:
    def __init__(self, promotion):
        self.idPromotion = promotion.idPromotion
        self.service_id = promotion.service.idTblService
        self.discount_percentage = promotion.discount_percentage
        self.start_date = promotion.start_date
        self.end_date = promotion.end_date
        self.is_active = promotion.is_active()

    def to_dict(self):
        return self.__dict__

class RendezVousServiceData:
    """Classe pour structurer un service dans un rendez-vous."""

    def __init__(self, service_instance):
        self.idRendezVousService = service_instance.idRendezVousService
        self.service = ServiceData(service_instance.service).to_dict()  # Utilise ServiceData pour les détails
        self.prix_applique = service_instance.prix_applique
        self.duree_estimee = service_instance.duree_estimee  # Durée estimée en minutes

    def to_dict(self):
        return self.__dict__


class RendezVousData:
    """Classe pour structurer un rendez-vous."""

    def __init__(self, rdv):
        self.idRendezVous = rdv.idRendezVous
        self.client = ClientData(rdv.client).to_dict()
        self.coiffeuse = CoiffeuseData(rdv.coiffeuse).to_dict()
        self.salon = SalonData(rdv.salon).to_dict()
        self.date_heure = rdv.date_heure.isoformat()
        self.statut = rdv.statut
        self.total_prix = rdv.total_prix
        self.duree_totale = rdv.duree_totale
        self.services = [RendezVousServiceData(s).to_dict() for s in rdv.rendez_vous_services.all()]

    def to_dict(self):
        return self.__dict__

stripe.api_key = settings_test.STRIPE_SECRET_KEY

class HoraireCoiffeuseData:
    def __init__(self, horaire):
        self.id = horaire.id
        self.coiffeuse_id = horaire.coiffeuse.idTblUser.idTblUser
        self.jour = horaire.jour  # int (0 = lundi)
        self.jour_label = horaire.get_jour_display()  # ex: "Lundi"
        self.heure_debut = horaire.heure_debut.strftime("%H:%M")
        self.heure_fin = horaire.heure_fin.strftime("%H:%M")

    def to_dict(self):
        return self.__dict__


class IndisponibiliteData:
    def __init__(self, indispo):
        self.id = indispo.id
        self.coiffeuse_id = indispo.coiffeuse.idTblUser.idTblUser

        # ✅ Sécurise le format, que ce soit déjà une string ou non
        self.date = indispo.date.isoformat() if hasattr(indispo.date, 'isoformat') else str(indispo.date)
        self.heure_debut = indispo.heure_debut.strftime("%H:%M") if hasattr(indispo.heure_debut, 'strftime') else str(indispo.heure_debut)
        self.heure_fin = indispo.heure_fin.strftime("%H:%M") if hasattr(indispo.heure_fin, 'strftime') else str(indispo.heure_fin)

        self.motif = indispo.motif

    def to_dict(self):
        return self.__dict__

class DisponibiliteManager:
    def __init__(self, coiffeuse):
        self.coiffeuse = coiffeuse

    def get_jours_ouverts(self):
        return list(
            TblHoraireCoiffeuse.objects.filter(coiffeuse=self.coiffeuse).values_list("jour", flat=True)
        )

    def get_dispos_pour_jour(self, date, duree_minutes=30):
        jour = date.weekday()  # 0 = lundi, ..., 6 = dimanche

        # 🔒 Vérifie si un horaire existe pour ce jour
        horaire = TblHoraireCoiffeuse.objects.filter(coiffeuse=self.coiffeuse, jour=jour).first()
        if not horaire:
            print("⛔️ Aucune horaire configurée ce jour-là")
            return []  # Salon fermé ce jour-là

        heure_debut = datetime.combine(date, horaire.heure_debut)
        heure_fin = datetime.combine(date, horaire.heure_fin)

        # ⏱ Génère les créneaux valides
        slots = []
        current = heure_debut

        while current + timedelta(minutes=duree_minutes) <= heure_fin:
            slot_debut = current
            slot_fin = current + timedelta(minutes=duree_minutes)

            # ❌ Indisponibilité exceptionnelle
            indispo = TblIndisponibilite.objects.filter(
                coiffeuse=self.coiffeuse,
                date=date,
                heure_debut__lt=slot_fin.time(),
                heure_fin__gt=slot_debut.time()
            ).exists()

            # ❌ Créneau déjà réservé
            rdv = TblRendezVous.objects.filter(
                coiffeuse=self.coiffeuse,
                date_heure__lt=slot_fin,
                date_heure__gte=slot_debut
            ).exists()

            print("🧪 Créneaux retournés :", [(d.strftime("%H:%M"), f.strftime("%H:%M")) for d, f in slots])

            if not indispo and not rdv:
                slots.append((slot_debut, slot_fin))

            current += timedelta(minutes=duree_minutes)

        return slots

class RendezVousManager:
    def __init__(self, coiffeuse_id):
        self.coiffeuse_id = coiffeuse_id

    def get_by_statut(self, statut):
        """
        🔍 Renvoie un queryset filtré par statut (et non archivé).
        """
        queryset = TblRendezVous.objects.filter(
            coiffeuse__idTblUser=self.coiffeuse_id,
            est_archive=False
        )
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset.order_by('-date_heure')

    def get_by_periode(self, periode, statut=None):
        """
        🔄 Renvoie un queryset filtré par période + statut (et non archivé).
        """
        today = now().date()

        if periode == "jour":
            start = today
            end = today + timedelta(days=1)
        elif periode == "semaine":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=7)
        elif periode == "mois":
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1)
        elif periode == "annee":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        else:
            return TblRendezVous.objects.none()  # aucun résultat

        queryset = TblRendezVous.objects.filter(
            coiffeuse__idTblUser=self.coiffeuse_id,
            date_heure__date__range=(start, end),
            est_archive=False
        )

        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset.order_by('-date_heure')
