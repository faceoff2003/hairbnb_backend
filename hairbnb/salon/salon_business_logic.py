from hairbnb.salon_services.salon_services_business_logic import ServiceData


class SalonData:
    def __init__(self, salon, filtered_services=None):
        self.idTblSalon = salon.idTblSalon

        # Gestion de la relation avec la coiffeuse (adaptation au nouveau modèle)
        # Vérifier si le salon a toujours une coiffeuse propriétaire principale
        if hasattr(salon, 'coiffeuse') and salon.coiffeuse:
            self.coiffeuse_id = salon.coiffeuse.idTblUser.idTblUser
        else:
            # Sinon, essayer de trouver la coiffeuse propriétaire via TblCoiffeuseSalon
            from hairbnb.models import TblCoiffeuseSalon
            proprietaire = TblCoiffeuseSalon.objects.filter(salon=salon, est_proprietaire=True).first()
            if proprietaire:
                self.coiffeuse_id = proprietaire.coiffeuse.idTblUser.idTblUser
            else:
                # Fallback si aucune coiffeuse propriétaire n'est trouvée
                self.coiffeuse_id = None

        # ✅ Soit on utilise les services filtrés (pagination), soit tous
        services_source = filtered_services if filtered_services is not None else salon.salon_service.all().order_by(
            'service__intitule_service')
        self.services = [ServiceData(service.service).to_dict() for service in services_source]

    def to_dict(self):
        return self.__dict__
