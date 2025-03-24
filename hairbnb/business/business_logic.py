from datetime import datetime, timedelta

import stripe

from hairbnb.models import TblClient, TblRendezVous, TblPaiement, TblHoraireCoiffeuse, TblIndisponibilite
from hairbnb_backend import settings_test


class CoiffeuseData:
    def __init__(self, coiffeuse):
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

# class ServiceData:
#     def __init__(self, service):
#         self.idTblService = service.idTblService
#         self.intitule_service = service.intitule_service
#         self.description = service.description
#
#         # Récupération du temps (via la table de jonction)
#         service_temps = service.service_temps.first()
#         self.temps_minutes = service_temps.temps.minutes if service_temps else None
#
#         # Récupération du prix (via la table de jonction)
#         service_prix = service.service_prix.first()
#         self.prix = service_prix.prix.prix if service_prix else None
#
#     def to_dict(self):
#         return self.__dict__

class SalonData:
    def __init__(self, salon):
        self.idTblSalon = salon.idTblSalon
        self.coiffeuse_id = salon.coiffeuse.idTblUser.idTblUser
        self.services = [ServiceData(service.service).to_dict() for service in salon.salon_service.all()]

    def to_dict(self):
        return self.__dict__

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

class CurrentUserData:
    def __init__(self, user):
        self.idTblUser = user.idTblUser
        self.uuid = user.uuid
        self.nom = user.nom
        self.prenom = user.prenom
        self.email = user.email
        self.numero_telephone = user.numero_telephone
        self.date_naissance = user.date_naissance
        self.sexe = user.sexe
        self.is_active = user.is_active
        self.photo_profil = user.photo_profil.url if user.photo_profil else None
        self.type = user.type  # Peut être "coiffeuse" ou "client"

        # Vérifier si c'est une coiffeuse ou un client et récupérer les données associées
        if user.type == "coiffeuse":
            try:
                coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
                self.extra_data = CoiffeuseData(coiffeuse).to_dict()  # Ajoute les infos de la coiffeuse
            except TblCoiffeuse.DoesNotExist:
                self.extra_data = None
        elif user.type == "client":
            try:
                client = TblClient.objects.get(idTblUser=user)
                self.extra_data = ClientData(client).to_dict()  # Ajoute les infos du client
            except TblClient.DoesNotExist:
                self.extra_data = None
        else:
            self.extra_data = None  # Aucune donnée complémentaire

    def to_dict(self):
        return self.__dict__

from hairbnb.models import TblCoiffeuse

class MinimalCoiffeuseData:
    def __init__(self, coiffeuse):
        user = coiffeuse.idTblUser  # Récupération de l'utilisateur associé à la coiffeuse
        self.idTblUser = user.idTblUser
        self.uuid = user.uuid
        self.nom = user.nom
        self.prenom = user.prenom
        self.photo_profil = user.photo_profil.url if user.photo_profil else None  # Vérification de la photo
        self.position = coiffeuse.position

    def to_dict(self):
        return self.__dict__

# class CartItemData:
from decimal import Decimal
from django.utils.timezone import now
from hairbnb.models import TblPromotion

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


# class CartItemData:
#     def __init__(self, cart_item):
#         self.id = cart_item.pk  # Utilisation de pk pour éviter l'erreur
#         self.service = ServiceData(cart_item.service).to_dict()
#         self.quantity = cart_item.quantity
#
#     def to_dict(self):
#         return self.__dict__



# class CartItemData:
#     def __init__(self, cart_item):
#         self.id = cart_item.id
#         self.service = ServiceData(cart_item.service).to_dict()  # ✅ Inclut prix_final
#         self.quantity = cart_item.quantity
#         self.total_price = self.service["prix_final"] * self.quantity  # ✅ Utilise le prix promo si actif
#
#     def to_dict(self):
#         return self.__dict__


class CartData:
    def __init__(self, cart):
        self.idTblCart = cart.idTblCart
        self.user = CurrentUserData(cart.user).to_dict()  # Réutilise CurrentUserData
        self.items = [CartItemData(item).to_dict() for item in cart.items.all()]
        self.total_price = cart.total_price()  # Méthode qui calcule le total

    def to_dict(self):
        return self.__dict__

from django.utils.timezone import now

class ServiceData:
    def __init__(self, service):
        self.idTblService = service.idTblService
        self.intitule_service = service.intitule_service
        self.description = service.description

        # 🔍 Récupération du temps
        service_temps = service.service_temps.first()
        self.temps_minutes = service_temps.temps.minutes if service_temps else None

        # 🔍 Récupération du prix
        service_prix = service.service_prix.first()
        self.prix = service_prix.prix.prix if service_prix else None

        # 🔍 Vérifie s'il y a une promotion active
        active_promo = service.promotions.filter(start_date__lte=now(), end_date__gte=now()).first()

        if active_promo:
            self.promotion = {
                "idPromotion": active_promo.idPromotion,
                "service_id": active_promo.service.idTblService,
                "discount_percentage": active_promo.discount_percentage,
                "start_date": active_promo.start_date.isoformat(),
                "end_date": active_promo.end_date.isoformat(),
                "is_active": active_promo.is_active()
            }
            # ✅ Calcul du prix final avec la réduction
            self.prix_final = self.prix * (1 - (active_promo.discount_percentage / 100))
        else:
            self.promotion = None
            self.prix_final = self.prix

    def to_dict(self):
        return self.__dict__

# class ServiceData:
#     def __init__(self, service):
#         self.idTblService = service.idTblService
#         self.intitule_service = service.intitule_service
#         self.description = service.description
#
#         # Récupération du temps (via la table de jonction)
#         service_temps = service.service_temps.first()
#         self.temps_minutes = service_temps.temps.minutes if service_temps else None
#
#         # Récupération du prix
#         service_prix = service.service_prix.first()
#         self.prix = service_prix.prix.prix if service_prix else None
#
#         # Récupération de la promotion active
#         active_promo = service.promotions.filter(start_date__lte=now(), end_date__gte=now()).first()
#         if active_promo:
#             self.discount_percentage = active_promo.discount_percentage
#             self.prix_final = self.prix * (1 - (self.discount_percentage / 100))
#         else:
#             self.discount_percentage = 0
#             self.prix_final = self.prix
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

class PaiementData:
    """Classe pour structurer un paiement."""

    def __init__(self, paiement):
        self.idPaiement = paiement.idPaiement
        self.rendez_vous = RendezVousData(paiement.rendez_vous).to_dict()
        self.montant_paye = paiement.montant_paye
        self.date_paiement = paiement.date_paiement.isoformat()
        self.methode = paiement.methode
        self.statut = paiement.statut  # Peut être 'en attente', 'payé', 'remboursé'

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def create_payment_intent(rendez_vous_id, methode_paiement):
        """
        Crée un PaymentIntent Stripe et retourne le client_secret.
        """
        try:
            rdv = TblRendezVous.objects.get(idRendezVous=rendez_vous_id)

            payment_intent = stripe.PaymentIntent.create(
                amount=int(rdv.total_prix * 100),  # Convertir en centimes
                currency="eur",
                payment_method_types=["card"],
                metadata={"rendez_vous_id": rdv.idRendezVous}
            )

            # Créer un paiement en attente
            paiement = TblPaiement.objects.create(
                rendez_vous=rdv,
                montant_paye=rdv.total_prix,
                methode=methode_paiement,
                statut="en attente"
            )

            return {"client_secret": payment_intent.client_secret, "paiement": PaiementData(paiement).to_dict()}

        except TblRendezVous.DoesNotExist:
            return {"error": "Rendez-vous non trouvé"}
        except Exception as e:
            return {"error": str(e)}

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



# class DisponibiliteManager:
#     def __init__(self, coiffeuse):
#         self.coiffeuse = coiffeuse
#
#     def get_jours_ouverts(self):
#         """Retourne la liste des jours où la coiffeuse travaille (0 = lundi, ..., 6 = dimanche)."""
#         return list(
#             TblHoraireCoiffeuse.objects.filter(coiffeuse=self.coiffeuse).values_list("jour", flat=True)
#         )
#
#     def get_dispos_pour_jour(self, date, duree_minutes=30):
#         """Retourne les créneaux disponibles d’un jour donné pour une durée spécifiée."""
#         jour = date.weekday()
#
#         # 🔒 Récupère l'horaire de travail du jour
#         horaire = TblHoraireCoiffeuse.objects.filter(coiffeuse=self.coiffeuse, jour=jour).first()
#         if not horaire:
#             return []  # Salon fermé ce jour-là
#
#         heure_debut = datetime.combine(date, horaire.heure_debut)
#         heure_fin = datetime.combine(date, horaire.heure_fin)
#
#         # 🧱 Création des créneaux
#         slots = []
#         current = heure_debut
#
#         while current + timedelta(minutes=duree_minutes) <= heure_fin:
#             slot_debut = current
#             slot_fin = current + timedelta(minutes=duree_minutes)
#
#             # 🔴 Indisponibilités exceptionnelles
#             if TblIndisponibilite.objects.filter(
#                 coiffeuse=self.coiffeuse,
#                 date=date,
#                 heure_debut__lt=slot_fin.time(),
#                 heure_fin__gt=slot_debut.time()
#             ).exists():
#                 current += timedelta(minutes=duree_minutes)
#                 continue
#
#             # 🔴 Rendez-vous existants
#             if TblRendezVous.objects.filter(
#                 coiffeuse=self.coiffeuse,
#                 date_heure__lt=slot_fin,
#                 date_heure__gte=slot_debut
#             ).exists():
#                 current += timedelta(minutes=duree_minutes)
#                 continue
#
#             # ✅ Créneau valide
#             slots.append((slot_debut, slot_fin))
#             current += timedelta(minutes=duree_minutes)
#
#         return slots
#
#     def get_dispos_semaine(self, start_date=None, duree_minutes=30):
#         """
#         Retourne un dictionnaire des créneaux disponibles pour les 7 prochains jours.
#         - start_date : date de départ (aujourd'hui par défaut)
#         - duree_minutes : durée des créneaux
#         """
#         if start_date is None:
#             start_date = datetime.today().date()
#
#         semaine = {}
#
#         for i in range(7):
#             jour = start_date + timedelta(days=i)
#             dispos = self.get_dispos_pour_jour(jour, duree_minutes)
#             if dispos:
#                 semaine[jour.strftime("%Y-%m-%d")] = [
#                     {
#                         "debut": d.strftime("%H:%M"),
#                         "fin": f.strftime("%H:%M")
#                     } for d, f in dispos
#                 ]
#
#         return semaine

# class DisponibiliteManager:
#     def __init__(self, coiffeuse):
#         self.coiffeuse = coiffeuse
#         self.horaires = TblHoraireCoiffeuse.objects.filter(coiffeuse=coiffeuse)
#         self.indispos = TblIndisponibilite.objects.filter(coiffeuse=coiffeuse)
#
#     def get_jours_ouverts(self):
#         return [h.jour for h in self.horaires]
#
#     def get_dispos_pour_jour(self, date, duree_service_minutes):
#         jour = date.weekday()
#         horaires = self.horaires.filter(jour=jour)
#
#         # Ignorer les indispos
#         indispos_du_jour = self.indispos.filter(date=date)
#
#         resultats = []
#         for h in horaires:
#             heure_debut = datetime.combine(date, h.heure_debut)
#             heure_fin = datetime.combine(date, h.heure_fin)
#
#             while (heure_debut + timedelta(minutes=duree_service_minutes)) <= heure_fin:
#                 slot_debut = heure_debut.time()
#                 slot_fin = (heure_debut + timedelta(minutes=duree_service_minutes)).time()
#
#                 # Vérifie chevauchement avec indispos
#                 conflict = any(
#                     i.heure_debut <= slot_debut <= i.heure_fin or
#                     i.heure_debut <= slot_fin <= i.heure_fin
#                     for i in indispos_du_jour
#                 )
#
#                 if not conflict:
#                     resultats.append((slot_debut, slot_fin))
#                 heure_debut += timedelta(minutes=15)
#
#         return resultats







