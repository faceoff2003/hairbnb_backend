from hairbnb.business.business_logic import ClientData
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
        self.sexe = user.sexe_ref.libelle if user.sexe_ref else None
        self.is_active = user.is_active
        self.photo_profil = user.photo_profil.url if user.photo_profil else None
        self.type = user.type_ref.libelle if user.type_ref else None

        # Ajouter les données d'adresse
        if user.adresse:
            self.adresse = {
                'numero': user.adresse.numero,
                'rue': user.adresse.rue.nom_rue if user.adresse.rue else None,
                'commune': user.adresse.rue.localite.commune if user.adresse.rue and user.adresse.rue.localite else None,
                'code_postal': user.adresse.rue.localite.code_postal if user.adresse.rue and user.adresse.rue.localite else None
            }
        else:
            self.adresse = None

        # Vérifier le type pour charger les données extra
        if self.type == "coiffeuse":
            try:
                coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
                self.extra_data = self._get_coiffeuse_data(coiffeuse)
            except TblCoiffeuse.DoesNotExist:
                self.extra_data = None
        elif self.type == "client":
            try:
                client = TblClient.objects.get(idTblUser=user)
                self.extra_data = ClientData(client).to_dict()
            except TblClient.DoesNotExist:
                self.extra_data = None
        else:
            self.extra_data = None

    def _get_coiffeuse_data(self, coiffeuse):
        """
        Récupère les données spécifiques à une coiffeuse avec le nouveau modèle.
        """
        data = {
            'nom_commercial': coiffeuse.nom_commercial,
        }

        # Récupérer le salon principal (salon où la coiffeuse est propriétaire)
        from hairbnb.models import TblCoiffeuseSalon
        salon_principal_relation = TblCoiffeuseSalon.objects.filter(
            coiffeuse=coiffeuse,
            est_proprietaire=True
        ).first()

        salon_principal_data = None
        if salon_principal_relation:
            salon = salon_principal_relation.salon
            salon_principal_data = {
                'idTblSalon': salon.idTblSalon,
                'nom_salon': salon.nom_salon,
                'slogan': salon.slogan,
                'a_propos': salon.a_propos,
                'logo_salon': salon.logo_salon.url if salon.logo_salon else None,
                'position': salon.position,
                'numero_tva': salon.numero_tva  # Maintenant directement dans le salon
            }

            # Ajouter l'adresse du salon si disponible
            if salon.adresse:
                salon_principal_data['adresse'] = {
                    'numero': salon.adresse.numero,
                    'rue': salon.adresse.rue.nom_rue if salon.adresse.rue else None,
                    'commune': salon.adresse.rue.localite.commune if salon.adresse.rue and salon.adresse.rue.localite else None,
                    'code_postal': salon.adresse.rue.localite.code_postal if salon.adresse.rue and salon.adresse.rue.localite else None
                }

        data['salon_principal'] = salon_principal_data

        # Ajouter tous les salons où la coiffeuse travaille
        salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)

        if salons_relations.exists():
            data['tous_salons'] = []
            for relation in salons_relations:
                salon_info = {
                    'idTblSalon': relation.salon.idTblSalon,
                    'nom_salon': relation.salon.nom_salon,
                    'est_proprietaire': relation.est_proprietaire,
                    'numero_tva': relation.salon.numero_tva  # TVA maintenant dans le salon
                }
                data['tous_salons'].append(salon_info)
        else:
            data['tous_salons'] = []

        return data

    def to_dict(self):
        return self.__dict__







# from hairbnb.business.business_logic import ClientData
# from hairbnb.models import TblCoiffeuse, TblClient
#
#
# class CurrentUserData:
#     def __init__(self, user):
#         self.idTblUser = user.idTblUser
#         self.uuid = user.uuid
#         self.nom = user.nom
#         self.prenom = user.prenom
#         self.email = user.email
#         self.numero_telephone = user.numero_telephone
#         self.date_naissance = user.date_naissance
#         self.sexe = user.sexe_ref.libelle if user.sexe_ref else None
#         self.is_active = user.is_active
#         self.photo_profil = user.photo_profil.url if user.photo_profil else None
#         self.type = user.type_ref.libelle if user.type_ref else None
#
#         # Ajouter les données d'adresse
#         if user.adresse:
#             self.adresse = {
#                 'numero': user.adresse.numero,
#                 'rue': user.adresse.rue.nom_rue if user.adresse.rue else None,
#                 'commune': user.adresse.rue.localite.commune if user.adresse.rue and user.adresse.rue.localite else None,
#                 'code_postal': user.adresse.rue.localite.code_postal if user.adresse.rue and user.adresse.rue.localite else None
#             }
#         else:
#             self.adresse = None
#
#         # Vérifier le type pour charger les données extra
#         if self.type == "coiffeuse":
#             try:
#                 coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
#                 self.extra_data = self._get_coiffeuse_data(coiffeuse)
#             except TblCoiffeuse.DoesNotExist:
#                 self.extra_data = None
#         elif self.type == "client":
#             try:
#                 client = TblClient.objects.get(idTblUser=user)
#                 self.extra_data = ClientData(client).to_dict()
#             except TblClient.DoesNotExist:
#                 self.extra_data = None
#         else:
#             self.extra_data = None
#
#     def _get_coiffeuse_data(self, coiffeuse):
#         """
#         Récupère les données spécifiques à une coiffeuse avec le nouveau modèle.
#         """
#         data = {
#             'nom_commercial': coiffeuse.nom_commercial,
#             'numero_tva': coiffeuse.numero_tva.numero_tva if coiffeuse.numero_tva else None
#         }
#
#         # Ajouter les données du salon principal (si existant)
#         if hasattr(coiffeuse, 'salon_direct'):
#             salon = coiffeuse.salon_direct
#             data['salon_principal'] = {
#                 'idTblSalon': salon.idTblSalon,
#                 'nom_salon': salon.nom_salon,
#                 'slogan': salon.slogan,
#                 'a_propos': salon.a_propos,
#                 'logo_salon': salon.logo_salon.url if salon.logo_salon else None,
#                 'position': salon.position
#             }
#
#             # Ajouter l'adresse du salon si disponible
#             if salon.adresse:
#                 data['salon_principal']['adresse'] = {
#                     'numero': salon.adresse.numero,
#                     'rue': salon.adresse.rue.nom_rue if salon.adresse.rue else None,
#                     'commune': salon.adresse.rue.localite.commune if salon.adresse.rue and salon.adresse.rue.localite else None,
#                     'code_postal': salon.adresse.rue.localite.code_postal if salon.adresse.rue and salon.adresse.rue.localite else None
#                 }
#
#             # Ajouter le numéro de TVA du salon si disponible
#             if salon.numero_tva:
#                 data['salon_principal']['numero_tva'] = salon.numero_tva.numero_tva
#
#         # Ajouter tous les salons où la coiffeuse travaille
#         from hairbnb.models import TblCoiffeuseSalon
#         salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)
#
#         if salons_relations.exists():
#             data['tous_salons'] = []
#             for relation in salons_relations:
#                 salon_info = {
#                     'idTblSalon': relation.salon.idTblSalon,
#                     'nom_salon': relation.salon.nom_salon,
#                     'est_proprietaire': relation.est_proprietaire
#                 }
#                 data['tous_salons'].append(salon_info)
#
#         return data
#
#     def to_dict(self):
#         return self.__dict__
#
#
#
#
#
#
#
# # from hairbnb.business.business_logic import ClientData
# # from hairbnb.models import TblCoiffeuse, TblClient, TblBoitePostale
# #
# #
# # class CurrentUserData:
# #     def __init__(self, user):
# #         self.idTblUser = user.idTblUser
# #         self.uuid = user.uuid
# #         self.nom = user.nom
# #         self.prenom = user.prenom
# #         self.email = user.email
# #         self.numero_telephone = user.numero_telephone
# #         self.date_naissance = user.date_naissance
# #         self.sexe = user.sexe_ref.libelle if user.sexe_ref else None
# #         self.is_active = user.is_active
# #         self.photo_profil = user.photo_profil.url if user.photo_profil else None
# #         self.type = user.type_ref.libelle if user.type_ref else None
# #
# #         # Ajouter les données d'adresse
# #         if user.adresse:
# #             self.adresse = {
# #                 'numero': user.adresse.numero,
# #                 'rue': user.adresse.rue.nom_rue if user.adresse.rue else None,
# #                 'commune': user.adresse.rue.localite.commune if user.adresse.rue and user.adresse.rue.localite else None,
# #                 'code_postal': user.adresse.rue.localite.code_postal if user.adresse.rue and user.adresse.rue.localite else None
# #             }
# #
# #             # Récupérer les boîtes postales
# #             boites_postales = TblBoitePostale.objects.filter(adresse=user.adresse)
# #             if boites_postales.exists():
# #                 self.adresse['boites_postales'] = [bp.numero_bp for bp in boites_postales]
# #             else:
# #                 self.adresse['boites_postales'] = []
# #         else:
# #             self.adresse = None
# #
# #         # Vérifier le type pour charger les données extra
# #         if self.type == "coiffeuse":
# #             try:
# #                 coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
# #                 self.extra_data = self._get_coiffeuse_data(coiffeuse)
# #             except TblCoiffeuse.DoesNotExist:
# #                 self.extra_data = None
# #         elif self.type == "client":
# #             try:
# #                 client = TblClient.objects.get(idTblUser=user)
# #                 self.extra_data = ClientData(client).to_dict()
# #             except TblClient.DoesNotExist:
# #                 self.extra_data = None
# #         else:
# #             self.extra_data = None
# #
# #     def _get_coiffeuse_data(self, coiffeuse):
# #         """
# #         Récupère les données spécifiques à une coiffeuse avec le nouveau modèle.
# #         """
# #         data = {
# #             'nom_commercial': coiffeuse.nom_commercial,
# #             'numero_tva': coiffeuse.numero_tva.numero_tva if coiffeuse.numero_tva else None
# #         }
# #
# #         # Ajouter les données du salon principal (si existant)
# #         if hasattr(coiffeuse, 'salon_direct'):
# #             salon = coiffeuse.salon_direct
# #             data['salon_principal'] = {
# #                 'idTblSalon': salon.idTblSalon,
# #                 'nom_salon': salon.nom_salon,
# #                 'slogan': salon.slogan,
# #                 'a_propos': salon.a_propos,
# #                 'logo_salon': salon.logo_salon.url if salon.logo_salon else None,
# #                 'position': salon.position
# #             }
# #
# #             # Ajouter l'adresse du salon si disponible
# #             if salon.adresse:
# #                 data['salon_principal']['adresse'] = {
# #                     'numero': salon.adresse.numero,
# #                     'rue': salon.adresse.rue.nom_rue if salon.adresse.rue else None,
# #                     'commune': salon.adresse.rue.localite.commune if salon.adresse.rue and salon.adresse.rue.localite else None,
# #                     'code_postal': salon.adresse.rue.localite.code_postal if salon.adresse.rue and salon.adresse.rue.localite else None
# #                 }
# #
# #             # Ajouter le numéro de TVA du salon si disponible
# #             if salon.numero_tva:
# #                 data['salon_principal']['numero_tva'] = salon.numero_tva.numero_tva
# #
# #         # Ajouter tous les salons où la coiffeuse travaille
# #         from hairbnb.models import TblCoiffeuseSalon
# #         salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)
# #
# #         if salons_relations.exists():
# #             data['tous_salons'] = []
# #             for relation in salons_relations:
# #                 salon_info = {
# #                     'idTblSalon': relation.salon.idTblSalon,
# #                     'nom_salon': relation.salon.nom_salon,
# #                     'est_proprietaire': relation.est_proprietaire
# #                 }
# #                 data['tous_salons'].append(salon_info)
# #
# #         return data
# #
# #     def to_dict(self):
# #         return self.__dict__
#
#
#
#
#
#
# # from hairbnb.business.business_logic import CoiffeuseData, ClientData
# # from hairbnb.models import TblCoiffeuse, TblClient
# #
# #
# # class CurrentUserData:
# #     def __init__(self, user):
# #         self.idTblUser = user.idTblUser
# #         self.uuid = user.uuid
# #         self.nom = user.nom
# #         self.prenom = user.prenom
# #         self.email = user.email
# #         self.numero_telephone = user.numero_telephone
# #         self.date_naissance = user.date_naissance
# #         self.sexe = user.sexe_ref.libelle if user.sexe_ref else None
# #         self.is_active = user.is_active
# #         self.photo_profil = user.photo_profil.url if user.photo_profil else None
# #         self.type = user.type_ref.libelle if user.type_ref else None
# #
# #         # Vérifier le type pour charger les données extra
# #         if self.type == "coiffeuse":
# #             try:
# #                 coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)
# #                 self.extra_data = CoiffeuseData(coiffeuse).to_dict()
# #             except TblCoiffeuse.DoesNotExist:
# #                 self.extra_data = None
# #         elif self.type == "client":
# #             try:
# #                 client = TblClient.objects.get(idTblUser=user)
# #                 self.extra_data = ClientData(client).to_dict()
# #             except TblClient.DoesNotExist:
# #                 self.extra_data = None
# #         else:
# #             self.extra_data = None
# #
# #     def to_dict(self):
# #         return self.__dict__
