from rest_framework import serializers
from hairbnb.models import TblSalon, TblCoiffeuseSalon


class SalonSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les salons avec géolocalisation et coiffeuses associées
    """
    # Récupérer les IDs des coiffeuses qui travaillent dans ce salon
    coiffeuse_ids = serializers.SerializerMethodField()
    # Récupérer les détails complets des coiffeuses
    coiffeuses_details = serializers.SerializerMethodField()
    # Récupérer les coordonnées de géolocalisation sous forme séparée
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    # Informations de base du salon
    nom = serializers.CharField(source='nom_salon')
    slogan = serializers.CharField()
    logo = serializers.ImageField(source='logo_salon')

    class Meta:
        model = TblSalon
        fields = [
            'idTblSalon',
            'nom',
            'slogan',
            'logo',
            'position',
            'latitude',
            'longitude',
            'coiffeuse_ids',
            'coiffeuses_details'
        ]

    def get_coiffeuse_ids(self, obj):
        """
        Récupère la liste des IDs des coiffeuses travaillant dans ce salon
        """
        # Utiliser la relation ManyToMany via TblCoiffeuseSalon
        relations = TblCoiffeuseSalon.objects.filter(salon=obj)
        return [relation.coiffeuse.idTblUser.idTblUser for relation in relations]

    def get_coiffeuses_details(self, obj):
        """
        Récupère les détails complets des coiffeuses travaillant dans ce salon
        """
        relations = TblCoiffeuseSalon.objects.filter(salon=obj)
        details = []
        for relation in relations:
            coiffeuse = relation.coiffeuse
            user = coiffeuse.idTblUser
            details.append({
                "idTblCoiffeuse": user.idTblUser,
                "idTblUser": user.idTblUser,
                "uuid": user.uuid,
                "nom": user.nom,
                "prenom": user.prenom,
                "role": user.get_role(),
                "type": user.get_type(),
                "est_proprietaire": relation.est_proprietaire,
                "nom_commercial": coiffeuse.nom_commercial
            })
        return details

    def get_latitude(self, obj):
        """
        Extrait la latitude de la position stockée
        """
        try:
            if obj.position:
                lat, _ = map(float, obj.position.split(','))
                return lat
        except (ValueError, TypeError):
            return None
        return None

    def get_longitude(self, obj):
        """
        Extrait la longitude de la position stockée
        """
        try:
            if obj.position:
                _, lon = map(float, obj.position.split(','))
                return lon
        except (ValueError, TypeError):
            return None
        return None



# class SalonSerializer(serializers.ModelSerializer):
#     """
#     Sérialiseur pour les salons avec géolocalisation et coiffeuses associées
#     """
#     # Récupérer les IDs des coiffeuses qui travaillent dans ce salon
#     coiffeuse_ids = serializers.SerializerMethodField()
#
#     # Récupérer les coordonnées de géolocalisation sous forme séparée
#     latitude = serializers.SerializerMethodField()
#     longitude = serializers.SerializerMethodField()
#
#     # Informations de base du salon
#     nom = serializers.CharField(source='nom_salon')
#     slogan = serializers.CharField()
#     logo = serializers.ImageField(source='logo_salon')
#
#     class Meta:
#         model = TblSalon
#         fields = [
#             'idTblSalon',
#             'nom',
#             'slogan',
#             'logo',
#             'position',
#             'latitude',
#             'longitude',
#             'coiffeuse_ids'
#         ]
#
#     def get_coiffeuse_ids(self, obj):
#         """
#         Récupère la liste des IDs des coiffeuses travaillant dans ce salon
#         """
#         # Utiliser la relation ManyToMany via TblCoiffeuseSalon
#         relations = TblCoiffeuseSalon.objects.filter(salon=obj)
#         return [relation.coiffeuse.idTblUser.idTblUser for relation in relations]
#
#     def get_latitude(self, obj):
#         """
#         Extrait la latitude de la position stockée
#         """
#         try:
#             if obj.position:
#                 lat, _ = map(float, obj.position.split(','))
#                 return lat
#         except (ValueError, TypeError):
#             return None
#         return None
#
#     def get_longitude(self, obj):
#         """
#         Extrait la longitude de la position stockée
#         """
#         try:
#             if obj.position:
#                 _, lon = map(float, obj.position.split(','))
#                 return lon
#         except (ValueError, TypeError):
#             return None
#         return None