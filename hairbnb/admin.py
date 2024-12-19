from django.contrib import admin
from .models import TblLocalite, TblRue, TblAdresse, TblUser, TblCoiffeuse, TblClient

admin.site.register(TblLocalite)
admin.site.register(TblRue)
admin.site.register(TblAdresse)
admin.site.register(TblUser)
admin.site.register(TblCoiffeuse)
admin.site.register(TblClient)
