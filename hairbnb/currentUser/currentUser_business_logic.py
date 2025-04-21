from hairbnb.business.business_logic import CoiffeuseData, ClientData
from hairbnb.models import TblCoiffeuse, TblClient


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
                coiffeuse = TblCoiffeuse.objects.get(idTblUsertbl=user)
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