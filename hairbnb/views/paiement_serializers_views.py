from rest_framework.decorators import api_view
from rest_framework.response import Response
from hairbnb.business.business_logic import PaiementData

@api_view(['POST'])
def create_payment_intent(request):
    """
    API pour créer un paiement Stripe.
    """
    try:
        rendez_vous_id = request.data.get("rendez_vous_id")
        methode_paiement = request.data.get("methode_paiement")

        result = PaiementData.create_payment_intent(rendez_vous_id, methode_paiement)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
