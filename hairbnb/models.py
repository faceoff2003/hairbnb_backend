from django.db import models
from django.utils.timezone import now
from hairbnb.services.upload_services import salon_image_upload_to
from decimal import Decimal

# Table pour gérer les localités
class TblLocalite(models.Model):
    idTblLocalite = models.AutoField(primary_key=True)
    commune = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.commune} ({self.code_postal})"


# Table pour gérer les rues
class TblRue(models.Model):
    idTblRue = models.AutoField(primary_key=True)
    nom_rue = models.CharField(max_length=255)
    localite = models.ForeignKey(
        TblLocalite, on_delete=models.CASCADE, related_name='rues'
    )

    class Meta:
        unique_together = ('nom_rue', 'localite')  # Unicité basée sur nom_rue et localite

    def __str__(self):
        return self.nom_rue


# Table pour gérer les adresses
class TblAdresse(models.Model):
    idTblAdresse = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10)
    boite_postale = models.CharField(max_length=10, blank=True, null=True)
    rue = models.ForeignKey(
        TblRue, on_delete=models.CASCADE, related_name='adresses'
    )

    def __str__(self):
        return f"{self.numero}, {self.boite_postale or ''}, {self.rue.nom_rue}, {self.rue.localite.commune}"


# Table utilisateur de base
class TblUser(models.Model):
    idTblUser = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=255, unique=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    type = models.CharField(
        max_length=10,
        choices=[('coiffeuse', 'Coiffeuse'), ('client', 'Client')]
    )
    sexe = models.CharField(
        max_length=6,
        choices=[('homme', 'Homme'), ('femme', 'Femme'), ('autre', 'Autre')]
    )
    numero_telephone = models.CharField(max_length=15)
    date_naissance = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    adresse = models.ForeignKey(
        'TblAdresse', on_delete=models.SET_NULL, null=True, related_name='utilisateurs'
    )
    photo_profil = models.ImageField(
        upload_to='photos/profils/',
        null=True,
        blank=True,
        default='photos/defaults/avatar.png'  # Avatar par défaut
    )

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.type})"


# Table pour les coiffeuses
class TblCoiffeuse(models.Model):
    idTblUser = models.OneToOneField(
        TblUser, on_delete=models.CASCADE, related_name='coiffeuse'
    )
    denomination_sociale = models.CharField(max_length=255, blank=True, null=True)
    tva = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = "Coiffeuse"
        verbose_name_plural = "Coiffeuses"

    def __str__(self):
        return f"Coiffeuse: {self.idTblUser.nom} {self.idTblUser.prenom}"

# Table pour les clients
class TblClient(models.Model):
    idTblUser = models.ForeignKey(
        TblUser,
        on_delete=models.CASCADE,
        related_name='clients',
        db_column='idTblUser'
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

# Table pour gérer les temps
class TblTemps(models.Model):
    idTblTemps = models.AutoField(primary_key=True, unique=True)
    minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.minutes} minutes"


# Table pour gérer les prix
class TblPrix(models.Model):
    idTblPrix = models.AutoField(primary_key=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, unique=True)  # ✅ UNIQUE

    def __str__(self):
        return f"{self.prix} €"


# class TblPrix(models.Model):
#     idTblPrix = models.AutoField(primary_key=True)
#     prix = models.DecimalField(max_digits=10, decimal_places=2)  # Prix en euros
#
#     def __str__(self):
#         return f"{self.prix} €"


# Table pour gérer les services
class TblService(models.Model):
    idTblService = models.AutoField(primary_key=True)
    intitule_service = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.intitule_service} €"


# Table pour gérer les salons
class TblSalon(models.Model):
    idTblSalon = models.AutoField(primary_key=True)
    coiffeuse = models.OneToOneField(
        'TblCoiffeuse', on_delete=models.CASCADE, related_name='salon'
    )
    slogan = models.CharField(max_length=255, blank=True, null=True)
    logo_salon = models.ImageField(
        upload_to='photos/logos/',
        null=True,
        blank=True,
        default='photos/defaults/logo_default.png'  # Logo par défaut
    )
    services = models.ManyToManyField(
        TblService, related_name='salons', through='TblSalonService'
    )
    def __str__(self):
        return f"Salon de {self.coiffeuse.idTblUser.nom} {self.coiffeuse.idTblUser.prenom}"


# Table de jonction pour relier les salons et les services
class TblSalonService(models.Model):
    idSalonService = models.AutoField(primary_key=True)
    salon = models.ForeignKey(TblSalon, on_delete=models.CASCADE, related_name="salon_service")
    service = models.ForeignKey(TblService, on_delete=models.CASCADE, related_name="salon_service")

    class Meta:
        unique_together = ('salon', 'service')  # Unicité entre un salon et un service

    def __str__(self):
        return f"Service '{self.service.intitule_service}' pour le salon '{self.salon.coiffeuse.idTblUser.nom}'"


# Table pour gérer les images de salon
class TblImageSalon(models.Model):
    idTblImageSalon = models.AutoField(primary_key=True)
    urlImages = models.ImageField(upload_to=salon_image_upload_to)  # Appel de la méthode externe
    salon = models.ForeignKey(
        TblSalon,
        on_delete=models.CASCADE,
        related_name='images'
    )

    def __str__(self):
        return f"Image du salon {self.salon.coiffeuse.idTblUser.nom} - {self.urlImages.name}"

    # Table de jonction pour relier les services et les temps
class TblServiceTemps(models.Model):
    idServiceTemps = models.AutoField(primary_key=True)
    service = models.ForeignKey(
        TblService, on_delete=models.CASCADE, related_name="service_temps"
    )
    temps = models.ForeignKey(
        TblTemps, on_delete=models.CASCADE, related_name="temps_services"
    )

    class Meta:
        unique_together = ('service', 'temps')

    def __str__(self):
        return f"Temps de {self.temps.minutes} minutes pour le service '{self.service.intitule_service}'"

    # Table de jonction pour relier les services et les prix
class TblServicePrix(models.Model):
    idServicePrix = models.AutoField(primary_key=True)
    service = models.ForeignKey(
        TblService, on_delete=models.CASCADE, related_name="service_prix"
    )
    prix = models.ForeignKey(
        TblPrix, on_delete=models.CASCADE, related_name="prix_services"
    )

    class Meta:
        unique_together = ('service',)  # Chaque service doit avoir une seule ligne dans TblServicePrix

    def __str__(self):
        return f"Prix de {self.prix.prix} € pour le service '{self.service.intitule_service}'"


# 📌 Modèle du panier pour chaque utilisateur
class TblCart(models.Model):
    idTblCart = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        TblUser, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        """ Calcule le total du panier """
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.nom} {self.user.prenom} - {self.items.count()} articles"


# 📌 Modèle pour les articles du panier
class TblCartItem(models.Model):
    idTblCartItem = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        TblCart, on_delete=models.CASCADE, related_name="items"
    )
    service = models.ForeignKey(
        TblService, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        """ Calcule le total pour cet article """
        prix_service = self.service.service_prix.first().prix.prix  # 🔥 Récupère le prix via la relation
        return self.quantity * prix_service

    def __str__(self):
        return f"{self.quantity} x {self.service.intitule_service} (Total: {self.total_price()}€)"

    class Meta:
        unique_together = ('cart', 'service')  # ✅ Un même service ne peut pas être ajouté plusieurs fois

class TblPromotion(models.Model):
    idPromotion = models.AutoField(primary_key=True)
    service = models.ForeignKey('TblService', on_delete=models.CASCADE, related_name="promotions")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    start_date = models.DateTimeField(default=now)  # Date de début de la promotion
    end_date = models.DateTimeField()  # Date de fin de la promotion

    def is_active(self):
        """
        Vérifie si la promotion est active en fonction de la date actuelle.
        """
        return self.start_date <= now() <= self.end_date

    def __str__(self):
        return f"Promotion de {self.discount_percentage}% pour {self.service.intitule_service} ({'Active' if self.is_active() else 'Expirée'})"

class TblRendezVous(models.Model):
    idRendezVous = models.AutoField(primary_key=True)
    client = models.ForeignKey('TblClient', on_delete=models.CASCADE, related_name='rendez_vous')
    coiffeuse = models.ForeignKey('TblCoiffeuse', on_delete=models.CASCADE, related_name='rendez_vous')
    salon = models.ForeignKey('TblSalon', on_delete=models.CASCADE, related_name='rendez_vous')
    date_heure = models.DateTimeField()
    statut = models.CharField(
        max_length=20,
        choices=[('en attente', 'En attente'), ('confirmé', 'Confirmé'), ('annulé', 'Annulé'), ('terminé', 'Terminé')],
        default='en attente'
    )
    total_prix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duree_totale = models.PositiveIntegerField(blank=True, null=True)  # ✅ Durée totale du RDV en minutes
    est_archive = models.BooleanField(default=False)


    def calculer_total(self):
        """ Calcule le prix total et la durée totale du RDV en fonction des services choisis """
        total_prix = 0
        total_duree = 0

        for service in self.rendez_vous_services.all():
            total_prix += service.prix_applique
            total_duree += service.duree_estimee  # 🔥 Ajout de la durée estimée

        self.total_prix = total_prix
        self.duree_totale = total_duree  # 🔥 Mise à jour de la durée totale
        self.save()

    def __str__(self):
        return f"RDV {self.idRendezVous} - {self.client.idTblUser.nom} ({self.date_heure})"


class TblRendezVousService(models.Model):
    idRendezVousService = models.AutoField(primary_key=True)
    rendez_vous = models.ForeignKey(
        'TblRendezVous', on_delete=models.CASCADE, related_name='rendez_vous_services'
    )
    service = models.ForeignKey(
        'TblService', on_delete=models.CASCADE, related_name='rendez_vous_services'
    )
    prix_applique = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )  # ✅ Prix appliqué au moment de la réservation
    duree_estimee = models.PositiveIntegerField(blank=True, null=True)  # 🔥 Durée totale du service

    class Meta:
        unique_together = ('rendez_vous', 'service')  # ✅ Un même service ne peut pas être ajouté plusieurs fois

    def save(self, *args, **kwargs):
        """ Applique le prix promo au moment de la réservation """
        if self.prix_applique is None:  # ✅ Si le prix n'est pas encore défini
            # 1️⃣ Récupérer le prix standard
            prix_service = TblServicePrix.objects.filter(service=self.service).first()
            prix_final = prix_service.prix.prix if prix_service else Decimal("0.00")

            # 2️⃣ Vérifier si une promotion est active AU MOMENT DE LA RESERVATION
            promo = TblPromotion.objects.filter(
                service=self.service,
                start_date__lte=now(),  # La promo est active au moment de la réservation
                end_date__gte=now()
            ).first()

            if promo:  # 🔥 Appliquer la réduction si une promo est trouvée
                reduction = (promo.discount_percentage / Decimal("100")) * prix_final
                prix_final -= reduction

            self.prix_applique = prix_final  # ✅ On enregistre le prix final

        # 3️⃣ Récupérer la durée estimée
        if not self.duree_estimee:
            temps_service = TblServiceTemps.objects.filter(service=self.service).first()
            self.duree_estimee = temps_service.temps.minutes if temps_service else 0

        super().save(*args, **kwargs)  # Appelle la sauvegarde originale

    def __str__(self):
        return f"{self.service.intitule_service} ({self.prix_applique} €) pour RDV {self.rendez_vous.idRendezVous}"

class TblPaiement(models.Model):
    idPaiement = models.AutoField(primary_key=True)
    rendez_vous = models.OneToOneField(
        'TblRendezVous', on_delete=models.CASCADE, related_name='paiement'
    )
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    methode = models.CharField(
        max_length=20,
        choices=[('carte', 'Carte'), ('cash', 'Cash'), ('paypal', 'PayPal')],
        default='carte'
    )
    statut = models.CharField(
        max_length=20,
        choices=[('en attente', 'En attente'), ('payé', 'Payé'), ('remboursé', 'Remboursé')],
        default='en attente'
    )

    def __str__(self):
        return f"Paiement de {self.montant_paye}€ pour RDV {self.rendez_vous.idRendezVous}"

class TblHoraireCoiffeuse(models.Model):
    coiffeuse = models.ForeignKey('TblCoiffeuse', on_delete=models.CASCADE, related_name='horaires')
    jour = models.IntegerField(choices=[(i, ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][i]) for i in range(7)])
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        unique_together = ('coiffeuse', 'jour')

    def __str__(self):
        return f"{self.coiffeuse.idTblUser.nom} - {self.get_jour_display()} : {self.heure_debut} - {self.heure_fin}"


# ✅ Indisponibilités exceptionnelles (vacances, congés, absences, etc.)
class TblIndisponibilite(models.Model):
    coiffeuse = models.ForeignKey('TblCoiffeuse', on_delete=models.CASCADE, related_name='indisponibilites')
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    motif = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.date} de {self.heure_debut} à {self.heure_fin} (motif: {self.motif})"

