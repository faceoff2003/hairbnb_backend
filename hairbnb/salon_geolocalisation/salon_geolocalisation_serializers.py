from rest_framework import serializers
from hairbnb.models import TblSalon, TblCoiffeuseSalon


class SalonSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les salons avec géolocalisation et coiffeuses associées
    """
    # Récupérer les IDs des coiffeuses qui travaillent dans ce salon
    coiffeuse_ids = serializers.SerializerMethodField()

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
            'coiffeuse_ids'
        ]

    def get_coiffeuse_ids(self, obj):
        """
        Récupère la liste des IDs des coiffeuses travaillant dans ce salon
        """
        # Utiliser la relation ManyToMany via TblCoiffeuseSalon
        relations = TblCoiffeuseSalon.objects.filter(salon=obj)
        return [relation.coiffeuse.idTblUser.idTblUser for relation in relations]

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