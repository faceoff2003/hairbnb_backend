from django.contrib import admin
from .models import TblLocalite, TblRue, TblAdresse, TblUser, TblCoiffeuse, TblClient, \
    TblSalon, TblImageSalon, TblService, TblPrix, TblTemps, TblSalonService, TblServicePrix, TblServiceTemps

admin.site.register(TblLocalite)
admin.site.register(TblRue)
admin.site.register(TblAdresse)
admin.site.register(TblUser)
admin.site.register(TblCoiffeuse)
admin.site.register(TblClient)
admin.site.register(TblSalon)
admin.site.register(TblImageSalon)
admin.site.register(TblService)
admin.site.register(TblPrix)
admin.site.register(TblTemps)
admin.site.register(TblSalonService)
admin.site.register(TblServicePrix)
admin.site.register(TblServiceTemps)