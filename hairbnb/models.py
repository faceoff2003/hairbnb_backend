from django.db import models

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
        TblAdresse, on_delete=models.SET_NULL, null=True, related_name='utilisateurs'
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




# from django.db import models
#
# # Table pour gérer les localités
# class TblLocalite(models.Model):
#     idTblLocalite = models.AutoField(primary_key=True)
#     commune = models.CharField(max_length=255)
#     code_postal = models.CharField(max_length=10)
#
#     def __str__(self):
#         return f"{self.commune} ({self.code_postal})"
#
# # Table pour gérer les rues
# class TblRue(models.Model):
#     idTblRue = models.AutoField(primary_key=True)
#     nom_rue = models.CharField(max_length=255, unique=True)
#     localite = models.ForeignKey(
#         TblLocalite, on_delete=models.CASCADE, related_name='rues'
#     )
#
#     def __str__(self):
#         return self.nom_rue
#
# # Table pour gérer les adresses
# class TblAdresse(models.Model):
#     idTblAdresse = models.AutoField(primary_key=True)
#     numero = models.CharField(max_length=10)
#     boite_postale = models.CharField(max_length=10, blank=True, null=True)  # Nouveau champ
#     rue = models.ForeignKey(
#         TblRue, on_delete=models.CASCADE, related_name='adresses'
#     )
#
#     def __str__(self):
#         return f"{self.numero}, {self.boite_postale or ''}, {self.rue.nom_rue}, {self.rue.localite.commune}"
#
#
# # Table utilisateur de base
# class TblUser(models.Model):
#     idTblUser = models.AutoField(primary_key=True)
#     uuid = models.CharField(max_length=255, unique=True)
#     nom = models.CharField(max_length=255)
#     prenom = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     type = models.CharField(
#         max_length=10,
#         choices=[('coiffeuse', 'Coiffeuse'), ('client', 'Client')]
#     )
#     sexe = models.CharField(
#         max_length=6,
#         choices=[('homme', 'Homme'), ('femme', 'Femme'), ('autre', 'Autre')]
#     )
#     numero_telephone = models.CharField(max_length=15)
#     date_naissance = models.DateField(null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#
#     adresse = models.ForeignKey(
#         TblAdresse, on_delete=models.SET_NULL, null=True, related_name='utilisateurs'
#     )
#
#     def __str__(self):
#         return f"{self.nom} {self.prenom} ({self.type})"
#
# class TblCoiffeuse(TblUser):
#     denomination_sociale = models.CharField(max_length=255, blank=True, null=True)
#     tva = models.CharField(max_length=20, blank=True, null=True)
#
#     #specialite = models.CharField(max_length=255, blank=True, null=True)
#     #experience = models.PositiveIntegerField(default=0)
#     #disponible = models.BooleanField(default=True)
#
#     # Champ géospatial pour les coordonnées (latitude/longitude)
#     position = models.CharField(max_length=512, blank=True, null=True)
#
#     class Meta:
#         verbose_name = "Coiffeuse"
#         verbose_name_plural = "Coiffeuses"
#
# # Table pour les clients
# class TblClient(TblUser):
#     #preferences = models.TextField(blank=True, null=True)
#
#     class Meta:
#         verbose_name = "Client"
#         verbose_name_plural = "Clients"
