from functools import wraps
from rest_framework.response import Response



"""
********************************************************************************
Un décorateur en Python est une fonction qui permet de modifier ou d'étendre 
le comportement d'autres fonctions ou méthodes sans changer leur code source. 
Il s'agit d'un outil puissant pour la programmation modulaire et réutilisable.
********************************************************************************
"""
def firebase_authenticated(view_func):
    """
    Décorateur qui vérifie si l'utilisateur est authentifié via Firebase.
    Si l'utilisateur n'est pas authentifié, renvoie une réponse 401.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user or not hasattr(request.user, 'uuid'):
            return Response({"detail": "Authentification requise"}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def is_owner(param_name="idUser"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # 🔍 Cherche dans kwargs PUIS dans request.data
            id_param = kwargs.get(param_name) or request.data.get(param_name)

            #print("🎯 USER CONNECTÉ :", user.idTblUser)
            #print("📥 PARAM ID     :", id_param)

            if not user or str(user.idTblUser) != str(id_param):
                return Response({"detail": "Accès interdit (non propriétaire)."}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# def is_owner(param_name="idUser"):
#     """
#     Décorateur qui vérifie si l'utilisateur est propriétaire de l'objet associé
#     au paramètre passé en argument.
#     Si l'utilisateur n'est pas propriétaire, renvoie une réponse 403.
#     """
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             user = request.user
#             id_param = kwargs.get(param_name)
#
#             #-------------------------------------------------------------------
#             print("🎯 USER CONNECTÉ :", user.idTblUser)
#             print("📥 PARAM ID     :", id_param)
#             # -------------------------------------------------------------------
#
#             if not user or str(user.idTblUser) != str(id_param):
#                 return Response({"detail": "Accès interdit (non propriétaire)."}, status=403)
#
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator