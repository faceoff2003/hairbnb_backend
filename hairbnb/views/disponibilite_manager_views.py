from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from hairbnb.models import TblCoiffeuse, TblUser
from hairbnb.business.business_logic import DisponibiliteManager

@api_view(['GET'])
def get_disponibilites_client(request, idUser):
    try:
        date_str = request.GET.get("date")
        duree = int(request.GET.get("duree", 30))  # durée par défaut : 30 min
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        print("📅 Date demandée :", date)
        print("⏱️ Durée du service :", duree, "minutes")

        # 1️⃣ Vérifier que l'utilisateur est bien une coiffeuse
        user = TblUser.objects.get(idTblUser=idUser, type='coiffeuse')
        print("🙋 Utilisateur trouvé :", user)

        # 2️⃣ Accéder à la coiffeuse via la relation OneToOne
        coiffeuse = user.coiffeuse  # ⚠️ nécessite related_name='coiffeuse' (ce que tu as mis)
        print("💇 Coiffeuse :", coiffeuse)

        # 3️⃣ Calcul des disponibilités
        manager = DisponibiliteManager(coiffeuse)
        jour = date.weekday()

        print("📆 Jour de la semaine :", jour)
        print("📌 Jours ouverts :", manager.get_jours_ouverts())

        dispos = manager.get_dispos_pour_jour(date, duree)

        print("✅ Créneaux disponibles :", dispos)
        return Response({
            "date": date_str,
            "disponibilites": [
                {
                    "debut": d.strftime("%H:%M"),
                    "fin": f.strftime("%H:%M")
                } for d, f in dispos
            ]
        })

    except TblUser.DoesNotExist:
        return Response({"error": "Aucun utilisateur de type coiffeuse trouvé avec cet ID."}, status=404)

    except TblCoiffeuse.DoesNotExist:
        return Response({"error": "Aucune coiffeuse liée à cet utilisateur."}, status=404)

    except Exception as e:
        import traceback
        print("❌ ERREUR :", e)
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)



# @api_view(['GET'])
# def get_disponibilites_client(request, coiffeuse_id):
#     try:
#         date_str = request.GET.get("date")
#         duree = int(request.GET.get("duree", 30))  # durée par défaut : 30 min
#         date = datetime.strptime(date_str, "%Y-%m-%d").date()
#
#         print("📅 Date demandée :", date)
#         print("⏱️ Durée du service :", duree, "minutes")
#
#         coiffeuse = TblCoiffeuse.objects.get(pk=coiffeuse_id)
#         print("💇 Coiffeuse :", coiffeuse)
#
#         manager = DisponibiliteManager(coiffeuse)
#         jour = date.weekday()
#
#         print("📆 Jour de la semaine :", jour)
#         print("📌 Jours ouverts :", manager.get_jours_ouverts())
#
#         dispos = manager.get_dispos_pour_jour(date, duree)
#
#         print("✅ Créneaux disponibles :", dispos)
#         return Response({
#             "date": date_str,
#             "disponibilites": [
#                 {
#                     "debut": d.strftime("%H:%M"),
#                     "fin": f.strftime("%H:%M")
#                 } for d, f in dispos
#             ]
#         })
#
#     except Exception as e:
#         import traceback
#         print("❌ ERREUR :", e)
#         traceback.print_exc()
#         return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_disponibilites_par_jour(request, coiffeuse_id):
    date_str = request.GET.get('date')  # exemple: "2025-05-01"
    duree = int(request.GET.get('duree', 30))

    if not date_str:
        return Response({"error": "Date requise (format YYYY-MM-DD)"}, status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({"error": "Format de date invalide"}, status=400)

    coiffeuse = TblCoiffeuse.objects.filter(user__idTblUser=coiffeuse_id).first()
    if not coiffeuse:
        return Response({"error": "Coiffeuse introuvable"}, status=404)

    manager = DisponibiliteManager(coiffeuse)
    slots = manager.get_dispos_pour_jour(date, duree)

    return Response({
        "date": date_str,
        "creneaux_disponibles": slots
    })