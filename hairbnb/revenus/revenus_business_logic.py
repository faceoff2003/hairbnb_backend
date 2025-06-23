# hairbnb/revenus/revenus_service.py

from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Q, Count
from django.utils import timezone
from hairbnb.models import TblPaiement, TblRendezVous, TblCoiffeuse, TblPaiementStatut


class RevenusService:
    """
    Service pour calculer les revenus des coiffeuses.
    Gère les filtres par période et les calculs HT/TTC.
    """

    # Taux de TVA français standard
    TAUX_TVA = Decimal('0.20')  # 20%

    @classmethod
    def get_revenus_coiffeuse(cls, coiffeuse_id, periode="mois", date_debut=None, date_fin=None, salon_id=None):
        """
        Récupère les revenus d'une coiffeuse selon les filtres spécifiés.

        Args:
            coiffeuse_id (int): ID de la coiffeuse
            periode (str): "jour", "semaine", "mois", "annee", "custom"
            date_debut (date): Date de début (pour période custom)
            date_fin (date): Date de fin (pour période custom)
            salon_id (int): ID du salon (optionnel)

        Returns:
            dict: Données structurées des revenus
        """
        try:
            # 1. Vérifier que la coiffeuse existe
            #coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
            coiffeuse = TblCoiffeuse.objects.get(idTblUser=coiffeuse_id)

            # 2. Calculer la période de filtrage
            dates = cls._calculer_periode(periode, date_debut, date_fin)

            # 3. Récupérer les paiements de la coiffeuse
            paiements_query = cls._get_paiements_coiffeuse(
                coiffeuse, dates['debut'], dates['fin'], salon_id
            )

            # 4. Calculer le résumé
            resume = cls._calculer_resume(paiements_query)

            # 5. Récupérer les détails des RDV
            details_rdv = cls._get_details_rdv(paiements_query)

            # 6. Calculer les statistiques
            statistiques = cls._calculer_statistiques(paiements_query)

            return {
                "success": True,
                "periode": periode,
                "date_debut": dates['debut'].strftime('%Y-%m-%d'),
                "date_fin": dates['fin'].strftime('%Y-%m-%d'),
                "resume": resume,
                "details_rdv": details_rdv,
                "statistiques": statistiques
            }

        except TblCoiffeuse.DoesNotExist:
            return {"success": False, "error": "Coiffeuse non trouvée"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def _calculer_periode(cls, periode, date_debut=None, date_fin=None):
        """
        Calcule les dates de début et fin selon la période demandée.

        Returns:
            dict: {'debut': date, 'fin': date}
        """
        today = timezone.now().date()

        if periode == "custom" and date_debut and date_fin:
            return {
                'debut': date_debut,
                'fin': date_fin
            }
        elif periode == "jour":
            return {
                'debut': today,
                'fin': today
            }
        elif periode == "semaine":
            # Du lundi au dimanche de cette semaine
            debut_semaine = today - timedelta(days=today.weekday())
            fin_semaine = debut_semaine + timedelta(days=6)
            return {
                'debut': debut_semaine,
                'fin': fin_semaine
            }
        elif periode == "mois":
            # Du 1er au dernier jour du mois courant
            debut_mois = today.replace(day=1)
            if today.month == 12:
                fin_mois = debut_mois.replace(year=today.year + 1, month=1) - timedelta(days=1)
            else:
                fin_mois = debut_mois.replace(month=today.month + 1) - timedelta(days=1)
            return {
                'debut': debut_mois,
                'fin': fin_mois
            }
        elif periode == "annee":
            # Du 1er janvier au 31 décembre de cette année
            debut_annee = today.replace(month=1, day=1)
            fin_annee = today.replace(month=12, day=31)
            return {
                'debut': debut_annee,
                'fin': fin_annee
            }
        else:
            # Par défaut : mois courant
            debut_mois = today.replace(day=1)
            if today.month == 12:
                fin_mois = debut_mois.replace(year=today.year + 1, month=1) - timedelta(days=1)
            else:
                fin_mois = debut_mois.replace(month=today.month + 1) - timedelta(days=1)
            return {
                'debut': debut_mois,
                'fin': fin_mois
            }

    @classmethod
    def _get_paiements_coiffeuse(cls, coiffeuse, date_debut, date_fin, salon_id=None):
        """
        Récupère les paiements payés de la coiffeuse dans la période donnée.

        Returns:
            QuerySet: Paiements filtrés
        """
        # Statut "payé"
        #statut_paye = TblPaiementStatut.objects.get(code="payé")

        try:
            statut_paye = TblPaiementStatut.objects.get(code="payé")
        except TblPaiementStatut.DoesNotExist:
            raise Exception("Statut de paiement 'payé' non configuré en base de données")

        # Query de base : paiements payés de la coiffeuse dans la période
        query = TblPaiement.objects.filter(
            statut=statut_paye,
            rendez_vous__coiffeuse=coiffeuse,
            date_paiement__date__gte=date_debut,
            date_paiement__date__lte=date_fin
        ).select_related(
            'rendez_vous',
            'rendez_vous__client',
            'rendez_vous__client__idTblUser',
            'rendez_vous__salon'
        ).prefetch_related(
            'rendez_vous__rendez_vous_services',
            'rendez_vous__rendez_vous_services__service'
        )

        # Filtre par salon si spécifié
        if salon_id:
            query = query.filter(rendez_vous__salon_id=salon_id)

        return query.order_by('-date_paiement')

    @classmethod
    def _calculer_resume(cls, paiements_query):
        """
        Calcule le résumé des revenus (totaux, nombre de RDV, etc.).

        Returns:
            dict: Résumé des données
        """
        # Calculs de base
        total_ttc = paiements_query.aggregate(
            total=Sum('montant_paye')
        )['total'] or Decimal('0.00')

        nb_rdv_payes = paiements_query.count()

        nb_clients_uniques = paiements_query.values(
            'rendez_vous__client'
        ).distinct().count()

        # Calculs TVA
        total_ht = total_ttc / (1 + cls.TAUX_TVA)
        tva = total_ttc - total_ht

        return {
            "nb_rdv_payes": nb_rdv_payes,
            "nb_clients_uniques": nb_clients_uniques,
            "total_ht": float(total_ht.quantize(Decimal('0.01'))),
            "total_ttc": float(total_ttc),
            "tva": float(tva.quantize(Decimal('0.01'))),
            "taux_tva": float(cls.TAUX_TVA * 100)  # En pourcentage
        }

    @classmethod
    def _get_details_rdv(cls, paiements_query):
        """
        Récupère les détails de chaque RDV payé.

        Returns:
            list: Liste des RDV avec détails
        """
        details = []

        for paiement in paiements_query:
            rdv = paiement.rendez_vous
            client = rdv.client.idTblUser if rdv.client else None

            # Services du RDV
            services = []
            total_services_ttc = Decimal('0.00')

            for rdv_service in rdv.rendez_vous_services.all():
                prix_ttc = rdv_service.prix_applique or Decimal('0.00')
                prix_ht = prix_ttc / (1 + cls.TAUX_TVA)

                services.append({
                    "nom": rdv_service.service.intitule_service,
                    "description": rdv_service.service.description,
                    "prix_ht": float(prix_ht.quantize(Decimal('0.01'))),
                    "prix_ttc": float(prix_ttc),
                    "duree_minutes": rdv_service.duree_estimee
                })

                total_services_ttc += prix_ttc

            # Calcul total HT
            total_ht = total_services_ttc / (1 + cls.TAUX_TVA)

            details.append({
                "rdv_id": rdv.idRendezVous,
                "date": rdv.date_heure.isoformat(),
                "client": {
                    "nom": client.nom if client else "Inconnu",
                    "prenom": client.prenom if client else "Inconnu",
                    "email": client.email if client else None
                } if client else None,
                "services": services,
                "total_ht": float(total_ht.quantize(Decimal('0.01'))),
                "total_ttc": float(total_services_ttc),
                "statut_rdv": rdv.statut,
                "salon": rdv.salon.nom_salon if rdv.salon else None
            })

        return details

    @classmethod
    def _calculer_statistiques(cls, paiements_query):
        """
        Calcule des statistiques utiles sur les revenus.

        Returns:
            dict: Statistiques diverses
        """
        if not paiements_query.exists():
            return {
                "service_plus_vendu": None,
                "jour_le_plus_rentable": None,
                "revenus_par_jour": {},
                "nb_services_differents": 0
            }

        # Service le plus vendu (simple implémentation)
        services_vendus = {}
        revenus_par_jour = {}

        for paiement in paiements_query:
            # Revenus par jour
            jour = paiement.date_paiement.strftime('%Y-%m-%d')
            if jour not in revenus_par_jour:
                revenus_par_jour[jour] = 0
            revenus_par_jour[jour] += float(paiement.montant_paye)

            # Services vendus
            for rdv_service in paiement.rendez_vous.rendez_vous_services.all():
                service_nom = rdv_service.service.intitule_service
                if service_nom not in services_vendus:
                    services_vendus[service_nom] = 0
                services_vendus[service_nom] += 1

        # Service le plus vendu
        service_plus_vendu = max(services_vendus.items(), key=lambda x: x[1])[0] if services_vendus else None

        # Jour le plus rentable
        jour_le_plus_rentable = max(revenus_par_jour.items(), key=lambda x: x[1])[0] if revenus_par_jour else None

        return {
            "service_plus_vendu": service_plus_vendu,
            "jour_le_plus_rentable": jour_le_plus_rentable,
            "revenus_par_jour": revenus_par_jour,
            "nb_services_differents": len(services_vendus)
        }