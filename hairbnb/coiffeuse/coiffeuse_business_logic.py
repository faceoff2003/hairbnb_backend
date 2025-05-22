class MinimalCoiffeuseData:
    """
    Classe pour récupérer et formater les informations essentielles d'une coiffeuse.
    Renvoie les URLs d'images sous forme de chemins relatifs pour une meilleure
    compatibilité avec l'application cliente.
    """

    def __init__(self, coiffeuse):
        # Récupération de l'utilisateur associé à la coiffeuse
        user = coiffeuse.idTblUser
        self.idTblUser = user.idTblUser
        self.uuid = user.uuid
        self.nom = user.nom
        self.prenom = user.prenom

        # Photo de profil : stocker le chemin relatif uniquement
        if user.photo_profil:
            self.photo_profil = user.photo_profil.url
        else:
            self.photo_profil = None

        # Informations spécifiques à la coiffeuse
        # Si position est un attribut de coiffeuse dans le modèle actuel
        self.nom_commercial = coiffeuse.nom_commercial

        # Si salon_direct existe dans le modèle actuel de coiffeuse
        if hasattr(coiffeuse, 'salon_direct') and coiffeuse.salon_direct:
            salon = coiffeuse.salon_direct
            self.salon = {
                'idTblSalon': salon.idTblSalon,
                'nom_salon': salon.nom_salon,
                'slogan': salon.slogan,
                'logo_salon': salon.logo_salon.url if salon.logo_salon else None,
                'position': salon.position if hasattr(salon, 'position') else None
            }
        else:
            self.salon = None

        # Ajouter les salons où la coiffeuse travaille
        from hairbnb.models import TblCoiffeuseSalon
        salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)

        if salons_relations.exists():
            self.autres_salons = []
            for relation in salons_relations:
                salon = relation.salon
                salon_info = {
                    'idTblSalon': salon.idTblSalon,
                    'nom_salon': salon.nom_salon,
                    'est_proprietaire': relation.est_proprietaire
                }
                self.autres_salons.append(salon_info)
        else:
            self.autres_salons = []

    def to_dict(self):
        """
        Convertit l'objet en dictionnaire.
        """
        return self.__dict__