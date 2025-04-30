# payment_service.py

import stripe
from hairbnb.models import TblRendezVous, TblRendezVousService
from hairbnb_backend import settings_test

stripe.api_key = settings_test.STRIPE_SECRET_KEY


class PaiementService:
    """
    Service métier responsable de la création d’un paiement Stripe
    pour un rendez-vous Hairbnb.

    Cette classe encapsule toute la logique métier :
    - récupération du rendez-vous et des services associés
    - calcul du montant total
    - création du PaymentIntent Stripe
    - renvoi du client_secret pour Flutter
    """

    @staticmethod
    def create_payment_intent(rendez_vous_id, methode_paiement='card'):
        """
        Crée un PaymentIntent Stripe pour un rendez-vous donné.

        Paramètres :
        ------------
        rendez_vous_id : int
            L’identifiant du rendez-vous concerné (TblRendezVous).
        methode_paiement : str
            La méthode de paiement (ex: 'card'), pour éventuelles évolutions.

        Retour :
        --------
        dict
            - Si succès : {
                "clientSecret": "...",
                "paymentIntentId": "..."
              }
            - Si erreur : { "error": "Message..." }
        """
        try:
            # 🔍 1. Récupération du rendez-vous
            rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)

            # 📦 2. Récupération des services liés au rendez-vous
            services = TblRendezVousService.objects.filter(rendez_vous=rendez_vous)

            if not services.exists():
                return {"error": "Aucun service associé à ce rendez-vous."}

            # 💰 3. Calcul du montant total
            montant_total = sum(s.prix_applique for s in services if s.prix_applique)
            montant_centimes = int(montant_total * 100)

            # ✅ 4. Création du PaymentIntent Stripe
            intent = stripe.PaymentIntent.create(
                amount=montant_centimes,
                currency='eur',
                automatic_payment_methods={'enabled': True},
                metadata={
                    "rendez_vous_id": str(rendez_vous.idRendezVous),
                    "client": rendez_vous.client.idTblUser.nom
                }
            )

            return {
                "clientSecret": intent.client_secret,
                "paymentIntentId": intent.id
            }

        except TblRendezVous.DoesNotExist:
            return {"error": "Rendez-vous introuvable."}

        except Exception as e:
            return {"error": f"Erreur lors de la création du paiement : {str(e)}"}






# from hairbnb.models import TblRendezVous, TblRendezVousService
# import stripe
# from hairbnb_backend import settings_test
#
# stripe.api_key = settings_test.STRIPE_SECRET_KEY
#
#
# class PaiementData:
#
#     @staticmethod
#     def create_payment_intent(rendez_vous_id, methode_paiement):
#         try:
#             # 🔍 Récupération du RDV
#             rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)
#
#             # 📦 Récupération des services liés
#             services = TblRendezVousService.objects.filter(rendez_vous=rendez_vous)
#
#             if not services.exists():
#                 return {"error": "Aucun service associé à ce rendez-vous."}
#
#             # 💰 Calcul du montant total depuis les prix appliqués
#             montant_total = sum(s.prix_applique for s in services if s.prix_applique)
#             montant_centimes = int(montant_total * 100)
#
#             # ✅ Création du PaymentIntent Stripe
#             intent = stripe.PaymentIntent.create(
#                 amount=montant_centimes,
#                 currency='eur',
#                 automatic_payment_methods={'enabled': True},
#                 metadata={
#                     "rendez_vous_id": str(rendez_vous.idRendezVous),
#                     "client": rendez_vous.client.idTblUser.nom
#                 }
#             )
#
#             return {
#                 "clientSecret": intent.client_secret,
#                 "paymentIntentId": intent.id
#             }
#
#         except TblRendezVous.DoesNotExist:
#             return {"error": "Rendez-vous introuvable."}
#         except Exception as e:
#             return {"error": str(e)}
