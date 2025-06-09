from rest_framework import serializers
from datetime import datetime, timedelta,date

from hairbnb.models import TblCoiffeuse, TblHoraireCoiffeuse, TblIndisponibilite, TblRendezVous


class CreneauDisponibleSerializer(serializers.Serializer):
    """
    Sérialise un créneau horaire disponible.
    """
    debut = serializers.TimeField(format='%H:%M')
    fin = serializers.TimeField(format='%H:%M')


class DisponibilitesClientSerializer(serializers.Serializer):
    """
    Sérialise les disponibilités d'une coiffeuse pour une date donnée.

    Calculé dynamiquement en fonction de :
    - Les horaires de travail de la coiffeuse
    - Ses indisponibilités exceptionnelles
    - Ses rendez-vous déjà réservés
    - La durée du service demandé
    """

    # Paramètres d'entrée (validation)
    coiffeuse_id = serializers.IntegerField()
    date = serializers.DateField()
    duree = serializers.IntegerField(min_value=1, max_value=480)  # Entre 1 min et 8h

    # Données de sortie
    disponibilites = CreneauDisponibleSerializer(many=True, read_only=True)

    def validate_coiffeuse_id(self, value):
        """Vérifie que la coiffeuse existe et est active."""
        try:
            coiffeuse = TblCoiffeuse.objects.select_related('idTblUser').get(
                idTblUser__idTblUser=value
            )

            # Vérifier que l'utilisateur est actif et du bon type
            user = coiffeuse.idTblUser
            if not user.is_active:
                raise serializers.ValidationError(f"La coiffeuse (ID: {value}) n'est pas active.")

            # Vérifier le type d'utilisateur
            if user.type_ref.libelle.lower() != 'coiffeuse':
                raise serializers.ValidationError(f"L'utilisateur (ID: {value}) n'est pas une coiffeuse.")

            return value

        except TblCoiffeuse.DoesNotExist:
            raise serializers.ValidationError(f"Coiffeuse avec l'ID {value} introuvable.")

    def validate_date(self, value):
        """Vérifie que la date n'est pas dans le passé."""
        if value < date.today():
            raise serializers.ValidationError("Impossible de réserver dans le passé.")
        return value

    def calculate_disponibilites(self, coiffeuse_id, target_date, duree_minutes):
        """
        Calcule les créneaux disponibles pour une coiffeuse à une date donnée.

        Args:
            coiffeuse_id (int): ID de la coiffeuse
            target_date (date): Date ciblée
            duree_minutes (int): Durée du service en minutes

        Returns:
            List[dict]: Liste des créneaux disponibles avec 'debut' et 'fin'
        """
        try:
            # 1️⃣ Récupérer la coiffeuse
            coiffeuse = TblCoiffeuse.objects.select_related('idTblUser').get(
                idTblUser__idTblUser=coiffeuse_id
            )

            # 2️⃣ Récupérer les horaires de travail pour ce jour de la semaine
            jour_semaine = target_date.weekday()  # 0=Lundi, 6=Dimanche

            horaires = TblHoraireCoiffeuse.objects.filter(
                coiffeuse=coiffeuse,
                jour=jour_semaine
            ).first()

            if not horaires:
                print(f"⚠️ Aucun horaire défini pour {coiffeuse.idTblUser.nom} le {jour_semaine}")
                return []

            # 3️⃣ Récupérer les indisponibilités exceptionnelles
            indisponibilites = TblIndisponibilite.objects.filter(
                coiffeuse=coiffeuse,
                date=target_date
            )

            # 4️⃣ Récupérer les rendez-vous déjà pris
            rdv_existants = TblRendezVous.objects.filter(
                coiffeuse=coiffeuse,
                date_heure__date=target_date,
                statut__in=['en attente', 'confirmé']  # Exclure annulés/terminés
            ).order_by('date_heure')

            # 5️⃣ Générer les créneaux libres
            creneaux_libres = self._generer_creneaux_libres(
                horaires, indisponibilites, rdv_existants,
                target_date, duree_minutes
            )

            print(f"✅ {len(creneaux_libres)} créneaux trouvés pour {coiffeuse.idTblUser.nom} le {target_date}")
            return creneaux_libres

        except TblCoiffeuse.DoesNotExist:
            print(f"❌ Coiffeuse {coiffeuse_id} introuvable")
            return []
        except Exception as e:
            print(f"❌ Erreur calcul disponibilités: {e}")
            return []

    def _generer_creneaux_libres(self, horaires, indisponibilites, rdv_existants, target_date, duree_minutes):
        """
        Génère la liste des créneaux libres en tenant compte de tous les obstacles.
        """
        creneaux_libres = []

        # Convertir la durée en timedelta
        duree_service = timedelta(minutes=duree_minutes)

        # Heure de début et fin de travail
        debut_travail = datetime.combine(target_date, horaires.heure_debut)
        fin_travail = datetime.combine(target_date, horaires.heure_fin)

        # Si la date est aujourd'hui, commencer à partir de maintenant
        maintenant = datetime.now()
        if target_date == date.today() and debut_travail < maintenant:
            # Arrondir à la prochaine demi-heure
            minutes_arrondies = ((maintenant.minute // 30) + 1) * 30
            debut_travail = maintenant.replace(minute=0, second=0, microsecond=0)
            debut_travail += timedelta(minutes=minutes_arrondies)

        # Créer une liste de tous les obstacles (indispos + rdv)
        obstacles = []

        # Ajouter les indisponibilités
        for indispo in indisponibilites:
            debut_obstacle = datetime.combine(target_date, indispo.heure_debut)
            fin_obstacle = datetime.combine(target_date, indispo.heure_fin)
            obstacles.append((debut_obstacle, fin_obstacle, "indisponibilité"))

        # Ajouter les rendez-vous existants
        for rdv in rdv_existants:
            debut_rdv = rdv.date_heure
            fin_rdv = debut_rdv + timedelta(minutes=rdv.duree_totale or 60)  # Durée par défaut 1h
            obstacles.append((debut_rdv, fin_rdv, f"RDV#{rdv.idRendezVous}"))

        # Trier les obstacles par heure de début
        obstacles.sort(key=lambda x: x[0])

        # Générer les créneaux entre les obstacles
        curseur = debut_travail

        for debut_obstacle, fin_obstacle, type_obstacle in obstacles:
            # Y a-t-il de la place avant cet obstacle ?
            if curseur + duree_service <= debut_obstacle:
                # Créer des créneaux de 30 minutes jusqu'à l'obstacle
                while curseur + duree_service <= debut_obstacle:
                    fin_creneau = curseur + duree_service
                    creneaux_libres.append({
                        'debut': curseur.time(),
                        'fin': fin_creneau.time()
                    })
                    curseur += timedelta(minutes=30)  # Créneaux par tranches de 30 min

            # Avancer le curseur après cet obstacle
            curseur = max(curseur, fin_obstacle)

        # Vérifier s'il reste de la place après le dernier obstacle
        while curseur + duree_service <= fin_travail:
            fin_creneau = curseur + duree_service
            creneaux_libres.append({
                'debut': curseur.time(),
                'fin': fin_creneau.time()
            })
            curseur += timedelta(minutes=30)

        return creneaux_libres