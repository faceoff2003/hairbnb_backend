# # Dans un fichier auth_backends.py
# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.models import User
# from hairbnb.models import TblUser
#
#
# class FirebaseBackend(BaseBackend):
#     def authenticate(self, request, firebase_uid=None):
#         if not firebase_uid:
#             return None
#
#         try:
#             # Recherchez l'utilisateur TblUser par firebase_uid
#             tbl_user = TblUser.objects.get(uuid=firebase_uid)
#
#             # Créez ou récupérez un utilisateur Django correspondant
#             try:
#                 user = User.objects.get(username=tbl_user.email)
#             except User.DoesNotExist:
#                 # Créer un utilisateur Django si nécessaire
#                 user = User.objects.create_user(
#                     username=tbl_user.email,
#                     email=tbl_user.email,
#                     password=None  # Pas besoin de mot de passe car l'auth est via Firebase
#                 )
#
#             # Ajouter une référence à TblUser
#             user.tbl_user = tbl_user
#             return user
#         except TblUser.DoesNotExist:
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None