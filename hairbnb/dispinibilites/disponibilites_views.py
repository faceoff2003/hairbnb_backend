from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from decorators.decorators import firebase_authenticated
from hairbnb.dispinibilites.disponibilities_serializers import DisponibilitesClientSerializer
from hairbnb.models import TblCoiffeuse


@api_view(['GET'])
@firebase_authenticated
def get_disponibilites_client(request, coiffeuse_id):
    """
    Récupère les disponibilités d'une coiffeuse pour une date donnée.

    URL: /api/get_disponibilites_client/{coiffeuse_id}/
    Paramètres GET:
    - date: Date au format YYYY-MM-DD
    - duree: Durée du service en minutes

    Exemple d'appel:
    GET /api/get_disponibilites_client/124/?date=2025-06-10&duree=158
    """
    print(f"🔄 === DÉBUT GET_DISPONIBILITES_CLIENT ===")
    print(f"🔄 CoiffeuseId: {coiffeuse_id}")
    print(f"🔄 Utilisateur connecté: {request.user}")
    print(f"🔄 Paramètres GET: {dict(request.GET)}")

    try:
        # 1️⃣ Récupérer et valider les paramètres
        date_param = request.GET.get('date')
        duree_param = request.GET.get('duree')

        # Validation des paramètres obligatoires
        if not date_param:
            print("❌ Paramètre 'date' manquant")
            return Response(
                {"error": "Le paramètre 'date' est obligatoire (format: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not duree_param:
            print("❌ Paramètre 'duree' manquant")
            return Response(
                {"error": "Le paramètre 'duree' est obligatoire (en minutes)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Conversion et validation des types
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            duree_minutes = int(duree_param)
        except ValueError as e:
            print(f"❌ Erreur de format: {e}")
            return Response(
                {"error": f"Format invalide - date: YYYY-MM-DD, durée: nombre entier. Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"✅ Date parsée: {target_date}")
        print(f"✅ Durée parsée: {duree_minutes} minutes")

        # 3️⃣ Validation avec le serializer
        data_to_validate = {
            'coiffeuse_id': coiffeuse_id,
            'date': target_date,
            'duree': duree_minutes
        }

        serializer = DisponibilitesClientSerializer(data=data_to_validate)

        if not serializer.is_valid():
            print(f"❌ Erreurs de validation: {serializer.errors}")
            return Response(
                {"error": "Données invalides", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        print("✅ Validation réussie")

        # 4️⃣ Calculer les disponibilités
        print(f"🔄 Calcul des disponibilités...")
        disponibilites = serializer.calculate_disponibilites(
            coiffeuse_id=int(coiffeuse_id),
            target_date=target_date,
            duree_minutes=duree_minutes
        )

        print(f"✅ {len(disponibilites)} créneaux calculés")

        # 5️⃣ Enrichir les données de réponse
        try:
            coiffeuse = TblCoiffeuse.objects.select_related('idTblUser').get(
                idTblUser__idTblUser=coiffeuse_id
            )
            coiffeuse_nom = f"{coiffeuse.idTblUser.prenom} {coiffeuse.idTblUser.nom}"
        except TblCoiffeuse.DoesNotExist:
            coiffeuse_nom = f"Coiffeuse #{coiffeuse_id}"

        # 6️⃣ Construire la réponse finale
        response_data = {
            "success": True,
            "coiffeuse_id": int(coiffeuse_id),
            "coiffeuse_nom": coiffeuse_nom,
            "date": date_param,
            "duree_demandee": duree_minutes,
            "disponibilites": disponibilites,
            "nb_creneaux": len(disponibilites),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Réponse construite: {len(disponibilites)} créneaux")
        print(f"✅ === FIN GET_DISPONIBILITES_CLIENT ===")

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"💥 ERREUR INATTENDUE: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"💥 Stack trace: {traceback.format_exc()}")

        return Response(
            {
                "error": "Erreur interne du serveur",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@firebase_authenticated
def get_creneaux_jour(request, coiffeuse_id):
    """
    Récupère les créneaux d'un jour spécifique.
    Utilisée par Flutter pour la sélection d'horaire.

    URL: /api/get_creneaux_jour/{coiffeuse_id}/
    """
    print(f"🔄 === GET_CRENEAUX_JOUR ===")
    print(f"🔄 CoiffeuseId: {coiffeuse_id}")

    try:
        # Mêmes paramètres que get_disponibilites_client
        date_param = request.GET.get('date')
        duree_param = request.GET.get('duree')

        if not date_param or not duree_param:
            return Response(
                {"error": "Paramètres 'date' et 'duree' obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Réutiliser la même logique
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        duree_minutes = int(duree_param)

        # Validation
        serializer = DisponibilitesClientSerializer(data={
            'coiffeuse_id': coiffeuse_id,
            'date': target_date,
            'duree': duree_minutes
        })

        if not serializer.is_valid():
            return Response(
                {"error": "Données invalides", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculer
        creneaux = serializer.calculate_disponibilites(
            coiffeuse_id=int(coiffeuse_id),
            target_date=target_date,
            duree_minutes=duree_minutes
        )

        # Format simplifié pour Flutter
        response_data = {
            "success": True,
            "creneaux": creneaux,
            "date": date_param
        }

        print(f"✅ {len(creneaux)} créneaux retournés pour le {date_param}")
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"❌ Erreur get_creneaux_jour: {e}")
        return Response(
            {"error": f"Erreur serveur: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )















# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from datetime import datetime
#
# from decorators.decorators import firebase_authenticated
# from hairbnb.dispinibilites.disponibilities_serializers import DisponibilitesClientSerializer
# from hairbnb.models import TblCoiffeuse
#
#
# @api_view(['GET'])
# @firebase_authenticated
# def get_disponibilites_client(request, coiffeuse_id):
#     """
#     Récupère les disponibilités d'une coiffeuse pour une date donnée.
#
#     URL: /api/get_disponibilites_client/{coiffeuse_id}/
#     Paramètres GET:
#     - date: Date au format YYYY-MM-DD
#     - duree: Durée du service en minutes
#
#     Exemple d'appel:
#     GET /api/get_disponibilites_client/124/?date=2025-06-10&duree=158
#     """
#     print(f"🔄 === DÉBUT GET_DISPONIBILITES_CLIENT ===")
#     print(f"🔄 CoiffeuseId: {coiffeuse_id}")
#     print(f"🔄 Utilisateur connecté: {request.user}")
#     print(f"🔄 Paramètres GET: {dict(request.GET)}")
#
#     try:
#         # 1️⃣ Récupérer et valider les paramètres
#         date_param = request.GET.get('date')
#         duree_param = request.GET.get('duree')
#
#         # Validation des paramètres obligatoires
#         if not date_param:
#             print("❌ Paramètre 'date' manquant")
#             return Response(
#                 {"error": "Le paramètre 'date' est obligatoire (format: YYYY-MM-DD)"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         if not duree_param:
#             print("❌ Paramètre 'duree' manquant")
#             return Response(
#                 {"error": "Le paramètre 'duree' est obligatoire (en minutes)"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # 2️⃣ Conversion et validation des types
#         try:
#             target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
#             duree_minutes = int(duree_param)
#         except ValueError as e:
#             print(f"❌ Erreur de format: {e}")
#             return Response(
#                 {"error": f"Format invalide - date: YYYY-MM-DD, durée: nombre entier. Erreur: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         print(f"✅ Date parsée: {target_date}")
#         print(f"✅ Durée parsée: {duree_minutes} minutes")
#
#         # 3️⃣ Validation avec le serializer
#         data_to_validate = {
#             'coiffeuse_id': coiffeuse_id,
#             'date': target_date,
#             'duree': duree_minutes
#         }
#
#         serializer = DisponibilitesClientSerializer(data=data_to_validate)
#
#         if not serializer.is_valid():
#             print(f"❌ Erreurs de validation: {serializer.errors}")
#             return Response(
#                 {"error": "Données invalides", "details": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         print("✅ Validation réussie")
#
#         # 4️⃣ Calculer les disponibilités
#         print(f"🔄 Calcul des disponibilités...")
#         disponibilites = serializer.calculate_disponibilites(
#             coiffeuse_id=int(coiffeuse_id),
#             target_date=target_date,
#             duree_minutes=duree_minutes
#         )
#
#         print(f"✅ {len(disponibilites)} créneaux calculés")
#
#         # 5️⃣ Enrichir les données de réponse
#         try:
#             coiffeuse = TblCoiffeuse.objects.select_related('idTblUser').get(
#                 idTblUser__idTblUser=coiffeuse_id
#             )
#             coiffeuse_nom = f"{coiffeuse.idTblUser.prenom} {coiffeuse.idTblUser.nom}"
#         except TblCoiffeuse.DoesNotExist:
#             coiffeuse_nom = f"Coiffeuse #{coiffeuse_id}"
#
#         # 6️⃣ Construire la réponse finale
#         response_data = {
#             "success": True,
#             "coiffeuse_id": int(coiffeuse_id),
#             "coiffeuse_nom": coiffeuse_nom,
#             "date": date_param,
#             "duree_demandee": duree_minutes,
#             "disponibilites": disponibilites,
#             "nb_creneaux": len(disponibilites),
#             "timestamp": datetime.now().isoformat()
#         }
#
#         print(f"✅ Réponse construite: {len(disponibilites)} créneaux")
#         print(f"✅ === FIN GET_DISPONIBILITES_CLIENT ===")
#
#         return Response(response_data, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         print(f"💥 ERREUR INATTENDUE: {type(e).__name__}: {str(e)}")
#         import traceback
#         print(f"💥 Stack trace: {traceback.format_exc()}")
#
#         return Response(
#             {
#                 "error": "Erreur interne du serveur",
#                 "details": str(e),
#                 "timestamp": datetime.now().isoformat()
#             },
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#
#
# @api_view(['GET'])
# @firebase_authenticated
# def get_creneaux_jour(request, coiffeuse_id):
#     """
#     Récupère les créneaux d'un jour spécifique.
#     Utilisée par Flutter pour la sélection d'horaire.
#
#     URL: /api/get_creneaux_jour/{coiffeuse_id}/
#     """
#     print(f"🔄 === GET_CRENEAUX_JOUR ===")
#     print(f"🔄 CoiffeuseId: {coiffeuse_id}")
#
#     try:
#         # Mêmes paramètres que get_disponibilites_client
#         date_param = request.GET.get('date')
#         duree_param = request.GET.get('duree')
#
#         if not date_param or not duree_param:
#             return Response(
#                 {"error": "Paramètres 'date' et 'duree' obligatoires"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Réutiliser la même logique
#         target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
#         duree_minutes = int(duree_param)
#
#         # Validation
#         serializer = DisponibilitesClientSerializer(data={
#             'coiffeuse_id': coiffeuse_id,
#             'date': target_date,
#             'duree': duree_minutes
#         })
#
#         if not serializer.is_valid():
#             return Response(
#                 {"error": "Données invalides", "details": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Calculer
#         creneaux = serializer.calculate_disponibilites(
#             coiffeuse_id=int(coiffeuse_id),
#             target_date=target_date,
#             duree_minutes=duree_minutes
#         )
#
#         # Format simplifié pour Flutter
#         response_data = {
#             "success": True,
#             "creneaux": creneaux,
#             "date": date_param
#         }
#
#         print(f"✅ {len(creneaux)} créneaux retournés pour le {date_param}")
#         return Response(response_data, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         print(f"❌ Erreur get_creneaux_jour: {e}")
#         return Response(
#             {"error": f"Erreur serveur: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#
#
#
#
#
#
#
#
#
#
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from datetime import datetime
# #
# # from decorators.decorators import firebase_authenticated, is_owner
# # from hairbnb.models import TblCoiffeuse, TblUser
# # from hairbnb.business.business_logic import DisponibiliteManager
# #
# # @api_view(['GET'])
# # #@firebase_authenticated
# # #@is_owner("idUser")
# # def get_disponibilites_client(request, idUser):
# #     try:
# #         date_str = request.GET.get("date")
# #         duree = int(request.GET.get("duree", 30))  # durée par défaut : 30 min
# #         date = datetime.strptime(date_str, "%Y-%m-%d").date()
# #
# #         #print("📅 Date demandée :", date)
# #         #print("⏱️ Durée du service :", duree, "minutes")
# #
# #         # 1️⃣ Vérifier que l'utilisateur est bien une coiffeuse
# #         user = TblUser.objects.get(idTblUser=idUser, type='coiffeuse')
# #         #print("🙋 Utilisateur trouvé :", user)
# #
# #         # 2️⃣ Accéder à la coiffeuse via la relation OneToOne
# #         coiffeuse = user.coiffeuse  # ⚠️ nécessite related_name='coiffeuse' (ce que tu as mis)
# #         #print("💇 Coiffeuse :", coiffeuse)
# #
# #         # 3️⃣ Calcul des disponibilités
# #         manager = DisponibiliteManager(coiffeuse)
# #         jour = date.weekday()
# #
# #         #print("📆 Jour de la semaine :", jour)
# #         #print("📌 Jours ouverts :", manager.get_jours_ouverts())
# #
# #         dispos = manager.get_dispos_pour_jour(date, duree)
# #
# #         #print("✅ Créneaux disponibles :", dispos)
# #         return Response({
# #             "date": date_str,
# #             "disponibilites": [
# #                 {
# #                     "debut": d.strftime("%H:%M"),
# #                     "fin": f.strftime("%H:%M")
# #                 } for d, f in dispos
# #             ]
# #         })
# #
# #     except TblUser.DoesNotExist:
# #         return Response({"error": "Aucun utilisateur de type coiffeuse trouvé avec cet ID."}, status=404)
# #
# #     except TblCoiffeuse.DoesNotExist:
# #         return Response({"error": "Aucune coiffeuse liée à cet utilisateur."}, status=404)
# #
# #     except Exception as e:
# #         import traceback
# #         print("❌ ERREUR :", e)
# #         traceback.print_exc()
# #         return Response({"error": str(e)}, status=500)
# #
# # #
# # # @api_view(['GET'])
# # # def get_disponibilites_par_jour(request, coiffeuse_id):
# # #     date_str = request.GET.get('date')  # exemple: "2025-05-01"
# # #     duree = int(request.GET.get('duree', 30))
# # #
# # #     if not date_str:
# # #         return Response({"error": "Date requise (format YYYY-MM-DD)"}, status=400)
# # #
# # #     try:
# # #         date = datetime.strptime(date_str, '%Y-%m-%d').date()
# # #     except ValueError:
# # #         return Response({"error": "Format de date invalide"}, status=400)
# # #
# # #     coiffeuse = TblCoiffeuse.objects.filter(user__idTblUser=coiffeuse_id).first()
# # #     if not coiffeuse:
# # #         return Response({"error": "Coiffeuse introuvable"}, status=404)
# # #
# # #     manager = DisponibiliteManager(coiffeuse)
# # #     slots = manager.get_dispos_pour_jour(date, duree)
# # #
# # #     return Response({
# # #         "date": date_str,
# # #         "creneaux_disponibles": slots
# # #     })