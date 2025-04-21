# hairbnb/business/business_logic.py

import stripe
from django.conf import settings
from hairbnb.models import TblRendezVous

stripe.api_key = settings.STRIPE_SECRET_KEY  # clé Stripe en mode test

class PaiementData:

    @staticmethod
    def create_payment_intent(rendez_vous_id, methode_paiement):
        try:
            # Récupérer le rendez-vous associé
            rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)

            # On suppose que le prix du service est accessible via le rendez-vous
            montant = int(rendez_vous.service.prix * 100)  # en centimes

            # Créer le PaymentIntent Stripe
            intent = stripe.PaymentIntent.create(
                amount=montant,
                currency='eur',  # ou 'mad', 'usd', etc.
                automatic_payment_methods={'enabled': True},
                metadata={
                    "rendez_vous_id": str(rendez_vous.id),
                    "client": rendez_vous.utilisateur.nom  # si dispo
                }
            )

            return {
                "clientSecret": intent.client_secret,
                "paymentIntentId": intent.id
            }

        except TblRendezVous.DoesNotExist:
            return {"error": "Rendez-vous introuvable."}
        except Exception as e:
            return {"error": str(e)}
