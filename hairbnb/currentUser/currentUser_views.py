from rest_framework.decorators import api_view
from rest_framework.response import Response
from decorators.decorators import firebase_authenticated
from hairbnb.currentUser.CurrentUser_serializer import CurrentUserSerializer


@api_view(['GET'])
@firebase_authenticated
def get_current_user(request):
    """
    Récupère les informations de l'utilisateur actuellement authentifié.
    Le décorateur firebase_authenticated garantit que request.user est correctement défini.
    """
    user = request.user

    # ✅ AJOUT DEBUG
    print(f"🔍 === get_current_user DEBUG ===")
    print(f"🔍 user: {user}")
    print(f"🔍 user.idTblUser: {getattr(user, 'idTblUser', 'N/A')}")
    print(f"🔍 user.type_ref: {getattr(user, 'type_ref', 'N/A')}")
    print(f"🔍 user.role: {getattr(user, 'role', 'N/A')}")

    if not user or not hasattr(user, 'uuid'):
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    # Passer le contexte de la requête au serializer pour construire des URLs absolues
    serializer = CurrentUserSerializer(user, context={'request': request})

    # ✅ AJOUT DEBUG RÉSULTAT
    result = serializer.data
    print(f"🔍 Résultat serializer: {result}")

    return Response({"status": "success", "user": result}, status=200)


@api_view(['GET'])
@firebase_authenticated
def get_user_by_id(request, id):
    """
    Récupère les informations d'un utilisateur spécifique par son ID.
    """
    from hairbnb.models import TblUser

    try:
        user = TblUser.objects.get(idTblUser=id)

        # ✅ AJOUT DEBUG
        print(f"🔍 === get_user_by_id DEBUG ===")
        print(f"🔍 user trouvé: {user}")
        print(f"🔍 user.idTblUser: {user.idTblUser}")
        print(f"🔍 user.type_ref: {user.type_ref}")
        print(f"🔍 user.role: {user.role}")

        # Passer le contexte de la requête au serializer pour construire des URLs absolues
        serializer = CurrentUserSerializer(user, context={'request': request})
        response_data = serializer.data.copy()

        # ✅ AJOUT DEBUG RÉSULTAT
        print(f"🔍 response_data après serializer: {response_data}")

    # try:
    #     user = TblUser.objects.get(idTblUser=id)
    #
    #     # Passer le contexte de la requête au serializer pour construire des URLs absolues
    #     serializer = CurrentUserSerializer(user, context={'request': request})
    #     response_data = serializer.data.copy()

        # Enrichir les données pour les coiffeuses
        if user.type_ref and user.type_ref.libelle == 'coiffeuse' and hasattr(user, 'coiffeuse'):
            coiffeuse = user.coiffeuse

            # Ajouter des informations détaillées sur les salons où travaille la coiffeuse
            from hairbnb.models import TblCoiffeuseSalon
            salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)

            if salons_relations.exists():
                salon_list = []
                salon_principal = None

                for relation in salons_relations:
                    salon_info = {
                        'idTblSalon': relation.salon.idTblSalon,
                        'nom_salon': relation.salon.nom_salon,
                        'slogan': relation.salon.slogan,
                        'logo_salon': relation.salon.logo_salon.url if relation.salon.logo_salon else None,
                        'numero_tva': relation.salon.numero_tva,
                        'est_proprietaire': relation.est_proprietaire
                    }

                    # Ajouter l'adresse du salon si disponible
                    if relation.salon.adresse:
                        salon_info['adresse'] = {
                            'numero': relation.salon.adresse.numero,
                            'rue': relation.salon.adresse.rue.nom_rue if relation.salon.adresse.rue else None,
                            'commune': relation.salon.adresse.rue.localite.commune if relation.salon.adresse.rue and relation.salon.adresse.rue.localite else None,
                            'code_postal': relation.salon.adresse.rue.localite.code_postal if relation.salon.adresse.rue and relation.salon.adresse.rue.localite else None
                        }

                    salon_list.append(salon_info)

                    # Identifier le salon principal (où la coiffeuse est propriétaire)
                    if relation.est_proprietaire:
                        salon_principal = salon_info

                # Mettre à jour les données de réponse
                if 'coiffeuse' in response_data:
                    response_data['coiffeuse']['tous_salons'] = salon_list
                    response_data['coiffeuse']['salon_principal'] = salon_principal

        return Response({"status": "success", "user": response_data}, status=200)

    except TblUser.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur introuvable"}, status=404)


# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from decorators.decorators import firebase_authenticated
# from hairbnb.currentUser.CurrentUser_serializer import CurrentUserSerializer
#
#
# @api_view(['GET'])
# #@firebase_authenticated
# def get_current_user(request):
#     """
#     Récupère les informations de l'utilisateur actuellement authentifié.
#     Le décorateur firebase_authenticated garantit que request.user est correctement défini.
#     """
#     user = request.user
#     if not user or not hasattr(user, 'uuid'):
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
#
#     # Passer le contexte de la requête au serializer pour construire des URLs absolues
#     serializer = CurrentUserSerializer(user, context={'request': request})
#
#     return Response({"status": "success", "user": serializer.data}, status=200)
#
#
# @api_view(['GET'])
# # @firebase_authenticated  # facultatif si accès public voulu
# def get_user_by_id(request, id):
#     """
#     Récupère les informations d'un utilisateur spécifique par son ID.
#     """
#     from hairbnb.models import TblUser
#     try:
#         user = TblUser.objects.get(idTblUser=id)
#
#         # Passer le contexte de la requête au serializer pour construire des URLs absolues
#         serializer = CurrentUserSerializer(user, context={'request': request})
#
#         # Enrichir la réponse avec la structure d'adresse simplifiée
#         response_data = serializer.data.copy()
#
#         # Ajouter les boîtes postales si elles existent
#         if user.adresse and hasattr(user.adresse, 'boites_postales'):
#             boites_postales = user.adresse.boites_postales.all()
#             if boites_postales.exists():
#                 bp_list = [bp.numero_bp for bp in boites_postales]
#                 if 'adresse' not in response_data:
#                     response_data['adresse'] = {}
#                 response_data['adresse']['boites_postales_simplifiees'] = bp_list
#
#         # Simplifier les informations sur la coiffeuse si l'utilisateur en est une
#         if user.type_ref and user.type_ref.libelle == 'coiffeuse' and hasattr(user, 'coiffeuse'):
#             coiffeuse = user.coiffeuse
#             # Ajouter des informations sur les salons où travaille la coiffeuse
#             if 'coiffeuse' in response_data and hasattr(coiffeuse, 'salons'):
#                 from hairbnb.models import TblCoiffeuseSalon
#                 salons_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)
#
#                 if salons_relations.exists():
#                     salon_list = []
#                     for relation in salons_relations:
#                         salon_info = {
#                             'idTblSalon': relation.salon.idTblSalon,
#                             'nom_salon': relation.salon.nom_salon,
#                             'est_proprietaire': relation.est_proprietaire
#                         }
#                         salon_list.append(salon_info)
#                     response_data['coiffeuse']['tous_salons'] = salon_list
#
#         return Response({"status": "success", "user": response_data}, status=200)
#
#     except TblUser.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur introuvable"}, status=404)
#
#
















# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
# from decorators.decorators import firebase_authenticated
# from hairbnb.currentUser.CurrentUser_serializer import CurrentUserSerializer
#
#
# @api_view(['GET'])
# @firebase_authenticated
# def get_current_user(request):
#     user = request.user
#
#     if not user or not hasattr(user, 'uuid'):
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
#
#     serializer = CurrentUserSerializer(user)
#     return Response({"status": "success", "user": serializer.data}, status=200)
#
#
# @api_view(['GET'])
# #@firebase_authenticated  # facultatif si accès public voulu
# def get_user_by_id(request, id):
#     from hairbnb.models import TblUser
#
#     try:
#         user = TblUser.objects.get(idTblUser=id)
#         serializer = CurrentUserSerializer(user)
#         return Response({"status": "success", "user": serializer.data}, status=200)
#     except TblUser.DoesNotExist:
#         return Response({"status": "error", "message": "Utilisateur introuvable"}, status=404)