# # views/paiement_views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import stripe
import traceback

from stripe import InvalidRequestError

from decorators.decorators import firebase_authenticated
from hairbnb.models import TblRendezVous, TblPaiement, TblPaiementStatut, TblMethodePaiement, TblRendezVousService, \
    TblTransaction
from hairbnb.payment.paiement_serializer import PaiementDetailSerializer, RefundSerializer
from hairbnb_backend import settings_test

stripe.api_key = settings_test.STRIPE_SECRET_KEY
endpoint_secret = settings_test.STRIPE_WEBHOOK_SECRET

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        rendez_vous_id = request.data.get("rendez_vous_id")
        print("📥 ID reçu: ", rendez_vous_id)

        if not rendez_vous_id:
            return Response({"error": "L'identifiant du rendez-vous est requis."}, status=400)

        rendez_vous = TblRendezVous.objects.filter(idRendezVous=rendez_vous_id).first()
        if not rendez_vous:
            return Response({"error": "Rendez-vous introuvable."}, status=404)

        services = TblRendezVousService.objects.filter(rendez_vous=rendez_vous)
        if not services.exists():
            return Response({"error": "Aucun service lié au rendez-vous."}, status=400)

        montant_total = sum(s.prix_applique for s in services if s.prix_applique)
        montant_centimes = int(montant_total * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f"Rendez-vous Hairbnb #{rendez_vous.idRendezVous}",
                    },
                    'unit_amount': montant_centimes,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://www.hairbnb.site/api/paiement-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://www.hairbnb.site/api/paiement-error?session_id={CHECKOUT_SESSION_ID}',
            metadata={
                'rendez_vous_id': rendez_vous.idRendezVous,
                'user_id': request.user.idTblUser,
                'email': request.user.email
            }
        )

        statut = TblPaiementStatut.objects.get(code='en_attente')
        methode = TblMethodePaiement.objects.get(code='card')

        paiement = TblPaiement.objects.create(
            rendez_vous=rendez_vous,
            utilisateur=request.user,
            montant_paye=montant_total,
            statut=statut,
            methode=methode,
            stripe_checkout_session_id=session.id
        )

        serializer = PaiementDetailSerializer(paiement)

        return Response({
            "checkout_url": session.url,
            "session_id": session.id,
            "paiement": serializer.data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@csrf_exempt
def stripe_webhook(request):
    print("\n\n🔔 WEBHOOK STRIPE REÇU 🔔")

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Correction de la variable d'environnement (si nécessaire)
    endpoint_secret = settings_test.STRIPE_WEBHOOK_SECRET

    print(f"📝 Signature: {sig_header}")
    print(f"🔑 Secret endpoint: {endpoint_secret[:10]}...")  # Affiche seulement le début pour sécurité

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print(f"✅ Webhook Stripe construit avec succès: {event['type']}")
    except ValueError as e:
        print(f"❌ Payload invalide: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Signature invalide: {e}")
        return HttpResponse(status=400)

    print(f"📦 Type d'événement: {event['type']}")

    # Imprimer l'objet complet pour les événements checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("🔍 Données de session complètes:")
        for key, value in session.items():
            print(f"  - {key}: {value}")

        checkout_session_id = session.get('id')
        payment_intent_id = session.get('payment_intent')

        print(f"🔎 Recherche de paiement avec session ID: {checkout_session_id}")
        paiement = TblPaiement.objects.filter(stripe_checkout_session_id=checkout_session_id).first()

        if paiement:
            print(f"✅ Paiement trouvé: {paiement.idTblPaiement}")

            try:
                # Récupération du statut "payé"
                statut_paye = TblPaiementStatut.objects.get(code="payé")
                print(f"🏷️ Statut 'payé' trouvé: {statut_paye.idTblPaiementStatut}")

                # Mise à jour du paiement
                paiement.statut = statut_paye
                paiement.stripe_payment_intent_id = payment_intent_id
                paiement.receipt_url = session.get('receipt_url')
                paiement.save()
                print("✅ Paiement mis à jour avec succès!")
            except TblPaiementStatut.DoesNotExist:
                print("❌ Statut 'payé' introuvable dans la base de données!")
                # Afficher tous les statuts disponibles
                print("📋 Statuts disponibles:")
                for statut in TblPaiementStatut.objects.all():
                    print(f"  - {statut.code}: {statut.libelle}")
            except Exception as e:
                print(f"❌ Erreur lors de la mise à jour du paiement: {e}")
                print(traceback.format_exc())
        else:
            print(f"❌ Aucun paiement trouvé avec session ID: {checkout_session_id}")
            # Afficher tous les paiements récents pour debug
            print("📋 Paiements récents:")
            for p in TblPaiement.objects.all().order_by('-date_paiement')[:5]:
                print(f"  - ID: {p.idTblPaiement}, Session: {p.stripe_checkout_session_id}")

    print("🏁 Fin du traitement webhook\n\n")
    return HttpResponse(status=200)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def check_payment_status(request, rendez_vous_id):
    try:
        print(f"🟡 Vérification statut pour RDV ID: {rendez_vous_id}")
        rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)
    except TblRendezVous.DoesNotExist:
        return Response({"error": "Rendez-vous introuvable."}, status=404)

    try:
        statut_paye = TblPaiementStatut.objects.get(code='payé')
        paiement = TblPaiement.objects.filter(rendez_vous=rendez_vous, statut=statut_paye).first()

        if paiement:
            print("🟢 Paiement trouvé ✅")
            return Response({"status": "payé", "details": PaiementDetailSerializer(paiement).data})
        else:
            print("🟠 Paiement non trouvé")
            return Response({"status": "non payé"}, status=200)

    except Exception as e:
        print("❌ Erreur dans check_payment_status:")
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=500)


def paiement_success(request):
    session_id = request.GET.get('session_id', '')
    print(f"✅ Page de succès appelée avec session_id: {session_id}")

    try:
        # Vérifiez si cette session existe dans votre base de données
        paiement = TblPaiement.objects.filter(stripe_checkout_session_id=session_id).first()
        if paiement:
            print(f"✅ Paiement trouvé en base de données: {paiement.idTblPaiement}")
            print(f"   Statut actuel: {paiement.statut.code if paiement.statut else 'Non défini'}")
            print(f"   RDV ID: {paiement.rendez_vous.idRendezVous}")

            # Récupérer le statut "payé"
            try:
                statut_paye = TblPaiementStatut.objects.get(code="payé")
            except TblPaiementStatut.DoesNotExist:
                try:
                    statut_paye = TblPaiementStatut.objects.get(code="paye")
                except TblPaiementStatut.DoesNotExist:
                    print("❌ Aucun statut 'payé' ou 'paye' trouvé dans la base de données!")
                    # Créer le statut si nécessaire
                    statut_paye = TblPaiementStatut.objects.create(code="payé", libelle="Payé")
                    print(f"✅ Statut 'payé' créé avec ID: {statut_paye.idTblPaiementStatut}")

            # Configurer l'API Stripe
            stripe.api_key = settings_test.STRIPE_SECRET_KEY

            try:
                # 1. Récupérer les informations de la session Checkout
                checkout_session = stripe.checkout.Session.retrieve(session_id)
                print(f"✅ Session Checkout récupérée: {checkout_session.id}")

                # Vérifier si le paiement est bien validé
                if checkout_session.payment_status == 'paid':
                    # Mettre à jour le statut du paiement
                    paiement.statut = statut_paye

                    # 2. Récupérer l'ID de PaymentIntent s'il n'est pas déjà enregistré
                    payment_intent_id = checkout_session.get('payment_intent')
                    if payment_intent_id and not paiement.stripe_payment_intent_id:
                        paiement.stripe_payment_intent_id = payment_intent_id
                        print(f"💳 Payment Intent ID mis à jour: {payment_intent_id}")

                    # 3. Récupérer l'email du client s'il est disponible
                    customer_email = checkout_session.get('customer_email')
                    if customer_email:
                        paiement.email_client = customer_email
                        print(f"📧 Email client mis à jour: {customer_email}")

                    # 4. Si des informations supplémentaires sont disponibles, essayer de les récupérer
                    # Mais ne bloquez pas si elles ne sont pas disponibles
                    try:
                        if payment_intent_id:
                            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                            # Récupérer la dernière charge si disponible
                            latest_charge = payment_intent.get('latest_charge')
                            if latest_charge and not paiement.stripe_charge_id:
                                paiement.stripe_charge_id = latest_charge
                                print(f"💵 Charge ID mis à jour: {latest_charge}")

                                # Essayer de récupérer l'URL du reçu
                                try:
                                    charge = stripe.Charge.retrieve(latest_charge)
                                    if charge.get('receipt_url') and not paiement.receipt_url:
                                        paiement.receipt_url = charge.get('receipt_url')
                                        print(f"🧾 Receipt URL mis à jour: {paiement.receipt_url}")
                                except Exception as e:
                                    print(
                                        f"ℹ️ Impossible de récupérer les détails de la charge (normal en mode test): {e}")

                            # Récupérer l'ID du client s'il est disponible
                            customer_id = payment_intent.get('customer')
                            if customer_id and not paiement.stripe_customer_id:
                                paiement.stripe_customer_id = customer_id
                                print(f"👤 Customer ID mis à jour: {customer_id}")

                                # Si l'email n'est pas encore défini, essayer de le récupérer du client
                                if not paiement.email_client:
                                    try:
                                        customer = stripe.Customer.retrieve(customer_id)
                                        if customer.get('email'):
                                            paiement.email_client = customer.get('email')
                                            print(
                                                f"📧 Email client récupéré depuis le customer: {paiement.email_client}")
                                    except Exception as e:
                                        print(
                                            f"ℹ️ Impossible de récupérer les détails du client (normal en mode test): {e}")
                    except Exception as e:
                        print(f"ℹ️ Impossible de récupérer des informations supplémentaires (normal en mode test): {e}")

                    # Utiliser l'email de l'utilisateur si disponible et qu'aucun email n'a été trouvé
                    if not paiement.email_client and paiement.utilisateur and paiement.utilisateur.email:
                        paiement.email_client = paiement.utilisateur.email
                        print(f"📧 Email client récupéré depuis l'utilisateur: {paiement.email_client}")

                    # Sauvegarder toutes les modifications
                    paiement.save()
                    print("✅ Paiement mis à jour avec succès!")

                    # Afficher toutes les informations mises à jour
                    print(f"📄 Informations de paiement finales:")
                    print(f"   - ID: {paiement.idTblPaiement}")
                    print(f"   - Statut: {paiement.statut.code}")
                    print(f"   - Payment Intent ID: {paiement.stripe_payment_intent_id or 'Non défini'}")
                    print(f"   - Charge ID: {paiement.stripe_charge_id or 'Non défini'}")
                    print(f"   - Customer ID: {paiement.stripe_customer_id or 'Non défini'}")
                    print(f"   - Email client: {paiement.email_client or 'Non défini'}")
                    print(f"   - Receipt URL: {paiement.receipt_url or 'Non défini'}")
                else:
                    print(f"⚠️ Le paiement n'est pas marqué comme payé dans Stripe: {checkout_session.payment_status}")

            except Exception as e:
                print(f"❌ Erreur lors de la récupération des informations depuis Stripe: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Aucun paiement trouvé avec session_id: {session_id}")

    except Exception as e:
        print(f"❌ Erreur dans paiement_success: {e}")
        import traceback
        traceback.print_exc()

    # Créer une page HTML de redirection au lieu d'utiliser HttpResponseRedirect
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paiement confirmé</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script>
            // Récupérer l'URL de base actuelle (domaine)
            var baseUrl = window.location.origin;
            var sessionId = "{session_id}";

            // Détection de l'appareil
            function isMobileDevice() {{
                return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            }}

            // Si c'est un appareil mobile, essayer d'ouvrir l'application
            if (isMobileDevice()) {{
                window.location.href = "hairbnb://paiement/success?session_id=" + sessionId;

                // Afficher un bouton après 2 secondes si l'app ne s'ouvre pas
                setTimeout(function() {{
                    if (document.getElementById('mobile-fallback')) {{
                        document.getElementById('mobile-fallback').style.display = 'block';
                    }}
                    document.getElementById('countdown').innerText = "L'application ne s'ouvre pas?";
                }}, 2000);
            }} else {{
                // Pour le web, rediriger vers l'application Flutter web avec hashtag (#)
                document.getElementById('countdown').innerText = "Redirection vers l'application web...";
                setTimeout(function() {{
                    window.location.href = baseUrl + "/#/paiement_success?session_id=" + sessionId;
                }}, 2000);
            }}
        </script>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px 20px; }}
            h1 {{ color: green; }}
            p {{ margin: 20px 0; }}
            .btn {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 25px; 
                   text-decoration: none; border-radius: 4px; margin-top: 20px; }}
            #mobile-fallback {{ display: none; }}
        </style>
    </head>
    <body>
        <h1>Paiement confirmé!</h1>
        <p>Votre réservation a été validée avec succès.</p>
        <p id="countdown">Redirection en cours...</p>

        <div id="mobile-fallback">
            <p>Si l'application ne s'ouvre pas automatiquement :</p>
            <a href="hairbnb://paiement/success?session_id={session_id}" class="btn">
                Ouvrir dans l'application
            </a>
        </div>

        <br>
        <a href="/#/paiement_success?session_id={session_id}" class="btn" style="margin-top: 20px; background: #2196F3;">
            Continuer sur le web
        </a>
    </body>
    </html>
    """

    return HttpResponse(html_response)


# views/refund_view.py

@api_view(['POST'])
@firebase_authenticated
def rembourser_paiement(request):
    serializer = RefundSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    id_paiement = data['id_paiement']
    montant = data.get('montant', None)

    try:
        paiement = TblPaiement.objects.get(idTblPaiement=id_paiement)
    except TblPaiement.DoesNotExist:
        return Response({"error": "Paiement introuvable"}, status=404)

    if not paiement.stripe_charge_id:
        return Response({"error": "Aucun identifiant de charge Stripe trouvé pour ce paiement."}, status=400)

    try:
        refund = stripe.Refund.create(
            charge=paiement.stripe_charge_id,
            amount=int(montant * 100) if montant else None
        )

        # 🔄 Création de la transaction
        TblTransaction.objects.create(
            paiement=paiement,
            type='remboursement',
            montant=montant or paiement.montant_paye,
            statut='effectué'
        )

        # ✅ Mise à jour du statut de paiement
        statut_rembourse = TblPaiementStatut.objects.get(code='remboursé')
        paiement.statut = statut_rembourse
        paiement.save()

        return Response({
            "message": "Remboursement effectué avec succès",
            "refund_id": refund.id
        })

    except InvalidRequestError as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@firebase_authenticated
def paiement_info(request, id_rendez_vous):
    try:
        paiement = TblPaiement.objects.filter(rendez_vous_id=id_rendez_vous).first()
        if paiement:
            return Response({
                'idTblPaiement': paiement.idTblPaiement,
                'montant_paye': float(paiement.montant_paye),
                'statut': paiement.statut.code,
                'stripe_payment_intent_id': paiement.stripe_payment_intent_id,
                'stripe_charge_id': paiement.stripe_charge_id,
            })
        return Response({"error": "Aucun paiement trouvé pour ce rendez-vous"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# -------------------------------------------Premiére essai fonctionnelle------------------------------

# def paiement_success(request):
#     session_id = request.GET.get('session_id', '')
#     print(f"✅ Page de succès appelée avec session_id: {session_id}")
#
#     try:
#         # Vérifiez si cette session existe dans votre base de données
#         paiement = TblPaiement.objects.filter(stripe_checkout_session_id=session_id).first()
#         if paiement:
#             print(f"✅ Paiement trouvé en base de données: {paiement.idTblPaiement}")
#             print(f"   Statut actuel: {paiement.statut.code if paiement.statut else 'Non défini'}")
#             print(f"   RDV ID: {paiement.rendez_vous.idRendezVous}")
#
#             # Vérifiez si ce paiement a déjà été marqué comme payé
#             if paiement.statut and paiement.statut.code in ["payé", "paye"]:
#                 print("💰 Ce paiement est déjà marqué comme payé!")
#             else:
#                 print("⚠️ Ce paiement n'est PAS marqué comme payé")
#
#                 # Essayons de mettre à jour le statut manuellement
#                 try:
#                     # Récupérer les infos de la session depuis Stripe
#                     stripe.api_key = settings_test.STRIPE_SECRET_KEY
#                     session = stripe.checkout.Session.retrieve(session_id)
#
#                     if session.payment_status == 'paid':
#                         print("💰 Session Stripe marquée comme payée, mise à jour du paiement...")
#
#                         # Récupérer le statut "payé"
#                         try:
#                             statut_paye = TblPaiementStatut.objects.get(code="payé")
#                         except TblPaiementStatut.DoesNotExist:
#                             try:
#                                 statut_paye = TblPaiementStatut.objects.get(code="paye")
#                             except TblPaiementStatut.DoesNotExist:
#                                 print("❌ Aucun statut 'payé' ou 'paye' trouvé dans la base de données!")
#                                 # Créer le statut si nécessaire
#                                 statut_paye = TblPaiementStatut.objects.create(code="payé", libelle="Payé")
#                                 print(f"✅ Statut 'payé' créé avec ID: {statut_paye.idTblPaiementStatut}")
#
#                         # Mettre à jour le paiement
#                         paiement.statut = statut_paye
#                         paiement.stripe_payment_intent_id = session.payment_intent
#                         paiement.save()
#                         print("✅ Paiement mis à jour avec succès!")
#                 except Exception as e:
#                     print(f"❌ Erreur lors de la mise à jour manuelle du paiement: {e}")
#         else:
#             print(f"❌ Aucun paiement trouvé avec session_id: {session_id}")
#
#     except Exception as e:
#         print(f"❌ Erreur dans paiement_success: {e}")
#
#     # Créer une page HTML de redirection au lieu d'utiliser HttpResponseRedirect
#     html_response = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Redirection...</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <script>
#             // Tentative de redirection via deep link
#             window.location.href = "hairbnb://paiement/success?session_id={session_id}";
#
#             // Redirection de secours après 3 secondes si le deep link échoue
#             setTimeout(function() {{
#                 if (document.getElementById('countdown')) {{
#                     document.getElementById('countdown').innerText = "Redirection automatique dans 0 secondes...";
#                     // Fermeture automatique
#                     window.close();
#                 }}
#             }}, 3000);
#         </script>
#         <style>
#             body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px 20px; }}
#             h1 {{ color: green; }}
#             p {{ margin: 20px 0; }}
#             .btn {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 25px;
#                    text-decoration: none; border-radius: 4px; margin-top: 20px; }}
#         </style>
#     </head>
#     <body>
#         <h1>Paiement confirmé!</h1>
#         <p>Votre réservation a été validée avec succès.</p>
#         <p id="countdown">Redirection automatique dans 3 secondes...</p>
#         <a href="hairbnb://paiement/success?session_id={session_id}" class="btn">
#             Cliquez ici pour retourner à l'application
#         </a>
#     </body>
#     </html>
#     """
#
#     return HttpResponse(html_response)
#
#
# def paiement_error(request):
#     session_id = request.GET.get('session_id', '')
#     print(f"⚠️ Page d'erreur appelée avec session_id: {session_id}")
#
#     # Créer une page HTML de redirection au lieu d'utiliser HttpResponseRedirect
#     html_response = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Redirection...</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <script>
#             // Tentative de redirection via deep link
#             window.location.href = "hairbnb://paiement/error?session_id={session_id}";
#
#             // Redirection de secours après 3 secondes si le deep link échoue
#             setTimeout(function() {{
#                 if (document.getElementById('countdown')) {{
#                     document.getElementById('countdown').innerText = "Redirection automatique dans 0 secondes...";
#                     // Fermeture automatique
#                     window.close();
#                 }}
#             }}, 3000);
#         </script>
#         <style>
#             body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px 20px; }}
#             h1 {{ color: red; }}
#             p {{ margin: 20px 0; }}
#             .btn {{ display: inline-block; background: #f44336; color: white; padding: 10px 25px;
#                    text-decoration: none; border-radius: 4px; margin-top: 20px; }}
#         </style>
#     </head>
#     <body>
#         <h1>Paiement annulé</h1>
#         <p>Votre paiement a été annulé ou a échoué.</p>
#         <p id="countdown">Redirection automatique dans 3 secondes...</p>
#         <a href="hairbnb://paiement/error?session_id={session_id}" class="btn">
#             Cliquez ici pour retourner à l'application
#         </a>
#     </body>
#     </html>
#     """
#
#     return HttpResponse(html_response)

# def paiement_success(request):
#     session_id = request.GET.get('session_id', '')
#     print(f"✅ Page de succès appelée avec session_id: {session_id}")
#
#     try:
#         # Vérifiez si cette session existe dans votre base de données
#         paiement = TblPaiement.objects.filter(stripe_checkout_session_id=session_id).first()
#         if paiement:
#             print(f"✅ Paiement trouvé en base de données: {paiement.idTblPaiement}")
#             print(f"   Statut actuel: {paiement.statut.code if paiement.statut else 'Non défini'}")
#             print(f"   RDV ID: {paiement.rendez_vous.idRendezVous}")
#
#             # Vérifiez si ce paiement a déjà été marqué comme payé
#             if paiement.statut and paiement.statut.code in ["payé", "paye"]:
#                 print("💰 Ce paiement est déjà marqué comme payé!")
#             else:
#                 print("⚠️ Ce paiement n'est PAS marqué comme payé")
#
#                 # Essayons de mettre à jour le statut manuellement
#                 try:
#                     # Récupérer les infos de la session depuis Stripe
#                     stripe.api_key = settings_test.STRIPE_SECRET_KEY
#                     session = stripe.checkout.Session.retrieve(session_id)
#
#                     if session.payment_status == 'paid':
#                         print("💰 Session Stripe marquée comme payée, mise à jour du paiement...")
#
#                         # Récupérer le statut "payé"
#                         try:
#                             statut_paye = TblPaiementStatut.objects.get(code="payé")
#                         except TblPaiementStatut.DoesNotExist:
#                             try:
#                                 statut_paye = TblPaiementStatut.objects.get(code="paye")
#                             except TblPaiementStatut.DoesNotExist:
#                                 print("❌ Aucun statut 'payé' ou 'paye' trouvé dans la base de données!")
#                                 # Créer le statut si nécessaire
#                                 statut_paye = TblPaiementStatut.objects.create(code="payé", libelle="Payé")
#                                 print(f"✅ Statut 'payé' créé avec ID: {statut_paye.idTblPaiementStatut}")
#
#                         # Mettre à jour le paiement
#                         paiement.statut = statut_paye
#                         paiement.stripe_payment_intent_id = session.payment_intent
#                         paiement.save()
#                         print("✅ Paiement mis à jour avec succès!")
#                 except Exception as e:
#                     print(f"❌ Erreur lors de la mise à jour manuelle du paiement: {e}")
#         else:
#             print(f"❌ Aucun paiement trouvé avec session_id: {session_id}")
#
#     except Exception as e:
#         print(f"❌ Erreur dans paiement_success: {e}")
#
#     # Continuer avec la redirection
#     return HttpResponseRedirect(f"hairbnb://paiement/success?session_id={session_id}")

def paiement_error(request):
    session_id = request.GET.get('session_id', '')
    print(f"⚠️ Page d'erreur appelée avec session_id: {session_id}")

    try:
        # Vérifier si cette session existe dans votre base de données
        paiement = TblPaiement.objects.filter(stripe_checkout_session_id=session_id).first()

        if paiement:
            print(f"✅ Paiement trouvé en base de données: {paiement.idTblPaiement}")
            print(f"   Statut actuel: {paiement.statut.code if paiement.statut else 'Non défini'}")
            print(f"   RDV ID: {paiement.rendez_vous.idRendezVous}")

            # Récupérer le statut "annulé" ou le créer si nécessaire
            try:
                statut_annule = TblPaiementStatut.objects.get(code="annulé")
            except TblPaiementStatut.DoesNotExist:
                try:
                    statut_annule = TblPaiementStatut.objects.get(code="annule")
                except TblPaiementStatut.DoesNotExist:
                    print("⚠️ Aucun statut 'annulé' ou 'annule' trouvé dans la base de données!")
                    # Créer le statut si nécessaire
                    statut_annule = TblPaiementStatut.objects.create(code="annulé", libelle="Annulé")
                    print(f"✅ Statut 'annulé' créé avec ID: {statut_annule.idTblPaiementStatut}")

            # Configurer l'API Stripe
            stripe.api_key = settings_test.STRIPE_SECRET_KEY

            try:
                # Vérifier le statut de la session dans Stripe
                checkout_session = stripe.checkout.Session.retrieve(session_id)
                print(f"✅ Session Checkout récupérée: {checkout_session.id}")
                print(f"   Statut de paiement Stripe: {checkout_session.payment_status}")

                # Mettre à jour le statut du paiement
                paiement.statut = statut_annule
                paiement.save()
                print(f"✅ Statut du paiement mis à jour à 'annulé'")

                # Mettre à jour le statut du rendez-vous associé
                rendez_vous = paiement.rendez_vous
                if rendez_vous:
                    rendez_vous.statut = 'annulé'
                    rendez_vous.save()
                    print(f"✅ Statut du rendez-vous #{rendez_vous.idRendezVous} mis à jour à 'annulé'")

            except Exception as e:
                print(f"❌ Erreur lors de la récupération des informations depuis Stripe: {e}")
                # En cas d'erreur, mettre quand même à jour le statut
                paiement.statut = statut_annule
                paiement.save()
                print(f"✅ Statut du paiement mis à jour à 'annulé' malgré l'erreur")
        else:
            print(f"⚠️ Aucun paiement trouvé avec session_id: {session_id}")

    except Exception as e:
        print(f"❌ Erreur dans paiement_error: {e}")
        import traceback
        traceback.print_exc()

    # Créer une page HTML de redirection au lieu d'utiliser HttpResponseRedirect
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paiement annulé</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script>
            // Tentative de redirection via deep link
            window.location.href = "hairbnb://paiement/error?session_id={session_id}";

            // Redirection de secours après 3 secondes si le deep link échoue
            setTimeout(function() {{
                if (document.getElementById('countdown')) {{
                    document.getElementById('countdown').innerText = "Redirection automatique dans 0 secondes...";
                    // Fermeture automatique
                    window.close();
                }}
            }}, 3000);
        </script>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px 20px; }}
            h1 {{ color: #e74c3c; }}
            p {{ margin: 20px 0; }}
            .btn {{ display: inline-block; background: #e74c3c; color: white; padding: 10px 25px; 
                   text-decoration: none; border-radius: 4px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>Paiement annulé</h1>
        <p>Votre paiement a été annulé ou a échoué.</p>
        <p id="countdown">Redirection automatique dans 3 secondes...</p>
        <a href="hairbnb://paiement/error?session_id={session_id}" class="btn">
            Cliquez ici pour retourner à l'application
        </a>
    </body>
    </html>
    """

    return HttpResponse(html_response)







# import traceback
#
# import stripe
# from django.http import HttpResponse, HttpResponseRedirect
# from django.utils import timezone
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from hairbnb.models import TblRendezVous, TblPaiement, TblPaiementStatut, TblMethodePaiement, TblRendezVousService
# from hairbnb.payment.payment_business_logic import PaiementService
# from hairbnb_backend import settings_test
#
#
#
# stripe.api_key = settings_test.STRIPE_SECRET_KEY
#
# @api_view(['POST'])
# #@permission_classes([IsAuthenticated])
# def create_checkout_session(request):
#     """
#     Crée une session Stripe Checkout et un enregistrement TblPaiement en statut 'en_attente'.
#     Retourne l'URL Stripe Checkout à ouvrir côté frontend.
#     """
#     try:
#
#
#         rendez_vous_id = request.data.get("rendez_vous_id")
#         rendez_vous = TblRendezVous.objects.filter(idRendezVous=rendez_vous_id).first()
#         print("📥 ID reçu: ", rendez_vous_id)
#
#
#         if not rendez_vous:
#             return Response({"error": "L'identifiant du rendez-vous est requis."}, status=400)
#
#         try:
#             TblRendezVous.objects.get(idRendezVous=rendez_vous_id)
#         except TblRendezVous.DoesNotExist:
#             return Response({"error": "Rendez-vous introuvable."}, status=404)
#
#         # Récupération des services
#         services = TblRendezVousService.objects.filter(rendez_vous=rendez_vous)
#         if not services.exists():
#             return Response({"error": "Aucun service lié au rendez-vous."}, status=400)
#
#         montant_total = sum(s.prix_applique for s in services if s.prix_applique)
#         montant_centimes = int(montant_total * 100)
#
#         # Création session Stripe Checkout
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {
#                         'name': f"Rendez-vous Hairbnb #{rendez_vous.idRendezVous}",
#                     },
#                     'unit_amount': montant_centimes,
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url='https://www.hairbnb.site/api/paiement-success?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url='https://www.hairbnb.site/api/paiement-error?session_id={CHECKOUT_SESSION_ID}',
#             metadata={
#                 'rendez_vous_id': rendez_vous.idRendezVous,
#                 'user_id': request.user.idTblUser,
#                 'email': request.user.email
#             }
#         )
#
#         # Statut & méthode
#         statut = TblPaiementStatut.objects.get(code='en_attente')
#         methode = TblMethodePaiement.objects.get(code='card')
#
#         # Enregistrement du paiement
#         TblPaiement.objects.create(
#             rendez_vous=rendez_vous,
#             utilisateur=request.user,
#             montant_paye=montant_total,
#             statut=statut,
#             methode=methode,
#             stripe_checkout_session_id=session.id
#         )
#
#         return Response({
#             "checkout_url": session.url,
#             "session_id": session.id
#         })
#
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)
#
#
# stripe.api_key = settings_test.STRIPE_SECRET_KEY
# endpoint_secret = settings_test.TRIPE_WEBHOOK_SECRET
#
# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = settings_test.TRIPE_WEBHOOK_SECRET
#
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)
#
#     # 🎯 Lorsqu'une session est complétée
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         checkout_session_id = session.get('id')
#         payment_intent_id = session.get('payment_intent')
#
#         # 🧠 Ici, tu dois retrouver ton paiement associé à cette session
#         paiement = TblPaiement.objects.filter(stripe_checkout_session_id=checkout_session_id).first()
#
#         if paiement:
#             statut_paye = TblPaiementStatut.objects.get(code="paye")
#             paiement.statut = statut_paye
#
#             paiement.stripe_payment_intent_id = payment_intent_id
#             paiement.save()
#
#     return HttpResponse(status=200)
#
#
#
# @api_view(['GET'])
# #@permission_classes([IsAuthenticated])
# def check_payment_status(request, rendez_vous_id):
#     try:
#         print(f"🟡 Vérification statut pour RDV ID: {rendez_vous_id}")
#         rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)
#     except TblRendezVous.DoesNotExist:
#         return Response({"error": "Rendez-vous introuvable."}, status=404)
#
#     try:
#         statut_paye = TblPaiementStatut.objects.get(code='payé')
#         paiement = TblPaiement.objects.filter(
#             rendez_vous=rendez_vous,
#             statut=statut_paye
#         ).first()
#
#         if paiement:
#             print("🟢 Paiement trouvé ✅")
#             return Response({"status": "payé"}, status=200)
#         else:
#             print("🟠 Paiement non trouvé")
#             return Response({"status": "non payé"}, status=200)
#
#     except Exception as e:
#         import traceback
#         print("❌ Erreur dans check_payment_status:")
#         print(traceback.format_exc())
#         return Response({"error": str(e)}, status=500)
#
#
#
#
# # @api_view(['GET'])
# # #@permission_classes([IsAuthenticated])
# # def check_payment_status(request, rendez_vous_id):
# #     """
# #     🔍 Vérifie si le paiement a été confirmé pour un rendez-vous donné.
# #
# #     Cette vue est appelée par l'application Flutter après redirection Stripe
# #     (ex: via un lien dynamique ou retour manuel) pour savoir si le paiement
# #     a bien été enregistré en base de données.
# #
# #     Elle permet d’éviter de :
# #     - relancer un paiement déjà effectué
# #     - rester bloqué sur l’écran de confirmation
# #     - créer des doublons de sessions Stripe
# #
# #     URL attendue :
# #     --------------
# #     GET /api/paiement/status/<rendez_vous_id>/
# #
# #     Headers :
# #     ---------
# #     Authorization: Bearer <JWT>
# #
# #     Réponses possibles :
# #     --------------------
# #     ✅ 200 OK - {"status": "payé"} → le paiement est validé
# #     ✅ 200 OK - {"status": "non payé"} → aucun paiement validé trouvé
# #     ❌ 404 Not Found - {"error": "Rendez-vous introuvable"}
# #
# #     Sécurité :
# #     ----------
# #     - Vue protégée par authentification JWT (IsAuthenticated)
# #     """
# #     try:
# #         rendez_vous = TblRendezVous.objects.get(pk=rendez_vous_id)
# #     except TblRendezVous.DoesNotExist:
# #         return Response({"error": "Rendez-vous introuvable."}, status=404)
# #
# #     statut_paye = TblPaiementStatut.objects.get(code='payé')
# #
# #     paiement = TblPaiement.objects.filter(
# #         rendez_vous=rendez_vous,
# #         statut=statut_paye
# #     ).first()
# #
# #     if paiement:
# #         return Response({"status": "payé"}, status=200)
# #     else:
# #         return Response({"status": "non payé"}, status=200)
#
# def paiement_success(request):
#     session_id = request.GET.get('session_id', '')
#     return HttpResponseRedirect(f"hairbnb://paiement/success?session_id={session_id}")
#
# def paiement_error(request):
#     session_id = request.GET.get('session_id', '')
#     return HttpResponseRedirect(f"hairbnb://paiement/error?session_id={session_id}")



















# import stripe
# from django.http import JsonResponse, HttpResponse
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
# from decorators.decorators import firebase_authenticated
# from hairbnb.models import TblRendezVous
# from hairbnb_backend import settings_test
#
#
# @api_view(['POST'])
# @firebase_authenticated
# #@is_owner("user_id")
# def create_payment_intent(request):
#     """
#     API pour créer un paiement Stripe.
#     """
#     try:
#         rendez_vous_id = request.data.get("rendez_vous_id")
#         methode_paiement = request.data.get("methode_paiement")
#
#         result = PaiementData.create_payment_intent(rendez_vous_id, methode_paiement)
#
#         if "error" in result:
#             print("🧪 Résultat PaiementData :", result)
#             return Response({"error": result["error"]}, status=400)
#
#         return Response(result, status=200)
#
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)
#
#
# stripe.api_key = settings_test.STRIPE_SECRET_KEY
#
#
# @api_view(['POST'])
# @firebase_authenticated
# def create_checkout_session(request):
#     try:
#         data = request.data
#         rendez_vous_id = data.get('rendez_vous_id')
#         # Utiliser idRendezVous au lieu de id pour la recherche
#         rendez_vous = TblRendezVous.objects.get(idRendezVous=rendez_vous_id)
#         # Utiliser le prix du rendez-vous
#         montant_en_centimes = int(rendez_vous.total_prix * 100)  # Convertir en centimes
#         nom_produit = f"Paiement Hairbnb - Rendez-vous #{rendez_vous_id}"
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {'name': nom_produit},
#                     'unit_amount': montant_en_centimes,
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             # Ajouter un paramètre à l'URL pour éviter les redirections en boucle
#             success_url='https://www.hairbnb.site/api/paiement-success?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url='https://www.hairbnb.site/api/paiement-error?session_id={CHECKOUT_SESSION_ID}',
#         )
#         return JsonResponse({'checkout_url': session.url})
#     except TblRendezVous.DoesNotExist:
#         return JsonResponse({'error': 'Rendez-vous non trouvé'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#
#
#
# def paiement_success(request):
#     print("Redirection vers l'application mobile - Paiement réussi")
#
#     # Vérifier si la redirection a déjà été effectuée (via un paramètre dans l'URL)
#     if request.GET.get('redirected') == 'true':
#         # Si déjà redirigé, afficher juste un message statique sans redirection
#         html = """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Paiement réussi</title>
#             <meta name="viewport" content="width=device-width, initial-scale=1">
#             <style>
#                 body { font-family: sans-serif; text-align: center; padding: 40px; }
#                 h1 { color: green; }
#             </style>
#         </head>
#         <body>
#             <h1>Paiement réussi!</h1>
#             <p>Vous pouvez fermer cette fenêtre.</p>
#         </body>
#         </html>
#         """
#     else:
#         # Première visite, afficher la page avec redirection
#         html = """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Paiement réussi</title>
#             <meta name="viewport" content="width=device-width, initial-scale=1">
#             <style>
#                 body { font-family: sans-serif; text-align: center; padding: 40px; }
#                 h1 { color: green; }
#                 .btn {
#                     background-color: #4CAF50;
#                     color: white;
#                     padding: 10px 20px;
#                     text-decoration: none;
#                     border-radius: 5px;
#                     display: inline-block;
#                     margin-top: 20px;
#                 }
#             </style>
#             <script>
#                 // Utiliser sessionStorage pour vérifier si la redirection a déjà été tentée
#                 if (!sessionStorage.getItem('redirected')) {
#                     sessionStorage.setItem('redirected', 'true');
#                     // Tente de rediriger après 3 secondes
#                     setTimeout(function() {
#                         window.location.href = 'hairbnb://paiement/success?redirected=true';
#                     }, 3000);
#                 }
#             </script>
#         </head>
#         <body>
#             <h1>Paiement réussi!</h1>
#             <p>Retour automatique vers l'application...</p>
#             <a href="hairbnb://paiement/success?redirected=true" class="btn">Retourner à l'application</a>
#         </body>
#         </html>
#         """
#
#     return HttpResponse(html)
#
# def paiement_error(request):
#     print("Redirection vers l'application mobile - Paiement échoué")
#
#     # Vérifier si la redirection a déjà été effectuée (via un paramètre dans l'URL)
#     if request.GET.get('redirected') == 'true':
#         # Si déjà redirigé, afficher juste un message statique sans redirection
#         html = """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Paiement annulé</title>
#             <meta name="viewport" content="width=device-width, initial-scale=1">
#             <style>
#                 body { font-family: sans-serif; text-align: center; padding: 40px; }
#                 h1 { color: red; }
#             </style>
#         </head>
#         <body>
#             <h1>Paiement annulé</h1>
#             <p>Vous pouvez fermer cette fenêtre.</p>
#         </body>
#         </html>
#         """
#     else:
#         # Première visite, afficher la page avec redirection
#         html = """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Paiement annulé</title>
#             <meta name="viewport" content="width=device-width, initial-scale=1">
#             <style>
#                 body { font-family: sans-serif; text-align: center; padding: 40px; }
#                 h1 { color: red; }
#                 .btn {
#                     background-color: #f44336;
#                     color: white;
#                     padding: 10px 20px;
#                     text-decoration: none;
#                     border-radius: 5px;
#                     display: inline-block;
#                     margin-top: 20px;
#                 }
#             </style>
#             <script>
#                 // Utiliser sessionStorage pour vérifier si la redirection a déjà été tentée
#                 if (!sessionStorage.getItem('redirected')) {
#                     sessionStorage.setItem('redirected', 'true');
#                     // Tente de rediriger après 3 secondes
#                     setTimeout(function() {
#                         window.location.href = 'hairbnb://paiement/echec?redirected=true';
#                     }, 3000);
#                 }
#             </script>
#         </head>
#         <body>
#             <h1>Paiement annulé</h1>
#             <p>Retour automatique vers l'application...</p>
#             <a href="hairbnb://paiement/echec?redirected=true" class="btn">Retourner à l'application</a>
#         </body>
#         </html>
#         """
#
#     return HttpResponse(html)
