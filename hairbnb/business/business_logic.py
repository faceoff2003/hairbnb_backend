from hairbnb.models import TblClient, TblCoiffeuse


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

class ServiceData:
    def __init__(self, service):
        self.idTblService = service.idTblService
        self.intitule_service = service.intitule_service
        self.description = service.description

        # Récupération du temps (via la table de jonction)
        service_temps = service.service_temps.first()
        self.temps_minutes = service_temps.temps.minutes if service_temps else None

        # Récupération du prix (via la table de jonction)
        service_prix = service.service_prix.first()
        self.prix = service_prix.prix.prix if service_prix else None

    def to_dict(self):
        return self.__dict__

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




