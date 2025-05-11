from django.contrib import admin
from hairbnb.models import (
    TblLocalite, TblRue, TblAdresse, TblCoiffeuse, TblClient,
    TblSalon, TblService, TblPrix, TblTemps, TblSalonService,
    TblServicePrix, TblServiceTemps, TblCart, TblCartItem,
    TblPromotion, TblRendezVous, TblPaiement, TblRendezVousService,
    TblIndisponibilite, TblHoraireCoiffeuse, TblSalonImage, TblAvis, TblFavorite, TblTransaction, TblPaiementStatut,
    TblMethodePaiement, TblEmailNotification, TblEmailType, TblEmailStatus, TblUser, TblRole, AIConversation, AIMessage
)

admin.site.register(TblLocalite)
admin.site.register(TblRue)
admin.site.register(TblAdresse)
admin.site.register(TblUser)
admin.site.register(TblRole)
admin.site.register(TblCoiffeuse)
admin.site.register(TblClient)
admin.site.register(TblSalon)
admin.site.register(TblSalonImage)    # ✅ nouveau
admin.site.register(TblAvis)          # ✅ nouveau
admin.site.register(TblService)
admin.site.register(TblPrix)
admin.site.register(TblTemps)
admin.site.register(TblSalonService)
admin.site.register(TblServicePrix)
admin.site.register(TblServiceTemps)
admin.site.register(TblCart)
admin.site.register(TblCartItem)
admin.site.register(TblPromotion)
admin.site.register(TblRendezVous)
admin.site.register(TblPaiement)
admin.site.register(TblRendezVousService)
admin.site.register(TblHoraireCoiffeuse)
admin.site.register(TblIndisponibilite)
admin.site.register(TblFavorite)
admin.site.register(TblTransaction)         # ✅ transaction liée à un paiement
admin.site.register(TblPaiementStatut)     # ✅ statut des paiements
admin.site.register(TblMethodePaiement)    # ✅ méthode de paiement
admin.site.register(TblEmailNotification)
admin.site.register(TblEmailType)
admin.site.register(TblEmailStatus)
admin.site.register(AIConversation)
admin.site.register(AIMessage)

