from _pydecimal import Decimal

from django.db import models
from django.utils.timezone import now
from hairbnb.services.upload_services import salon_image_upload_to


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

