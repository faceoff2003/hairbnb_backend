# views.py - Système d'avis avec décorateurs Firebase

import logging
from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated, is_owner, is_admin, is_owner_coiffeuse
from hairbnb.avis.avis_serializers import RdvEligibleAvisSerializer, AvisCreateSerializer, AvisDetailSerializer, \
    MesAvisSerializer, AvisListSerializer, AdminAvisSerializer, CoiffeuseAvisClientSerializer
from hairbnb.models import (
    TblAvis, TblRendezVous, TblClient,
    TblSalon, TblAvisStatut, TblCoiffeuse, TblCoiffeuseSalon
)

logger = logging.getLogger(__name__)


# 1️⃣ VIEW POUR RÉCUPÉRER LES RDV ÉLIGIBLES AUX AVIS
#@csrf_exempt
@api_view(['GET'])
@firebase_authenticated
def mes_rdv_avis_en_attente(request):
    """
    Récupère les RDV éligibles aux avis pour le client connecté
    Utilisé pour afficher la notification "X avis en attente" sur la home page
    """
    try:
        # Récupérer le client depuis l'utilisateur Firebase connecté
        client = get_object_or_404(TblClient, idTblUser__uuid=request.user.uuid)

        # Calculer la limite de temps (2h après la fin théorique du RDV)
        maintenant = timezone.now()

        # RDV terminés du client
        rdvs_termines = TblRendezVous.objects.filter(
            client=client,
            statut='terminé'
        ).exclude(
            # Exclure ceux qui ont déjà un avis
            idRendezVous__in=TblAvis.objects.values_list('rendez_vous__idRendezVous', flat=True)
        )

        # Filtrer ceux éligibles (2h après la fin)
        rdvs_eligibles = []
        for rdv in rdvs_termines:
            fin_theorique = rdv.date_heure + timedelta(minutes=rdv.duree_totale or 60)
            if maintenant >= fin_theorique + timedelta(hours=2):
                rdvs_eligibles.append(rdv)

        # Sérialiser les résultats
        serializer = RdvEligibleAvisSerializer(rdvs_eligibles, many=True)

        return Response({
            "success": True,
            "message": f"{len(rdvs_eligibles)} avis en attente",
            "count": len(rdvs_eligibles),
            "rdv_eligibles": serializer.data
        })

    except TblClient.DoesNotExist:
        return Response({
            "success": False,
            "message": "Client non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans mes_rdv_avis_en_attente: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 2️⃣ VIEW POUR CRÉER UN AVIS
@api_view(['POST'])
@firebase_authenticated
@is_owner(param_name="client_uuid", use_uuid=True)
def creer_avis(request):
    """
    Crée un nouvel avis pour un RDV
    Sécurisé : vérifie que le RDV appartient au client connecté
    """
    try:
        # Le paramètre client_uuid sera vérifié par le décorateur is_owner
        # On l'ajoute aux données pour que le décorateur puisse le vérifier
        request.data['client_uuid'] = request.user.uuid

        # Créer le serializer avec le contexte de la requête
        serializer = AvisCreateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            avis = serializer.save()

            # Retourner l'avis créé avec tous les détails
            response_serializer = AvisDetailSerializer(avis)

            return Response({
                "success": True,
                "message": "Avis créé avec succès !",
                "avis": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": "Erreurs de validation",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans creer_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur lors de la création de l'avis: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 3️⃣ VIEW POUR LISTER SES PROPRES AVIS
@api_view(['GET'])
@firebase_authenticated
@is_owner(param_name="client_uuid", use_uuid=True)
def mes_avis(request):
    """
    Liste tous les avis donnés par le client connecté
    Historique personnel des avis
    """
    try:
        # Le paramètre client_uuid sera vérifié par le décorateur
        client_uuid = request.query_params.get('client_uuid', request.user.uuid)

        # Récupérer le client
        client = get_object_or_404(TblClient, idTblUser__uuid=client_uuid)

        # Récupérer tous les avis du client
        avis = TblAvis.objects.filter(client=client).order_by('-date')

        # Pagination optionnelle
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        avis_paginated = avis[start:end]
        serializer = MesAvisSerializer(avis_paginated, many=True)

        return Response({
            "success": True,
            "message": f"{avis.count()} avis trouvés",
            "avis": serializer.data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": avis.count(),
                "has_next": end < avis.count()
            }
        })

    except TblClient.DoesNotExist:
        return Response({
            "success": False,
            "message": "Client non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans mes_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 4️⃣ VIEW POUR MODIFIER UN AVIS
@api_view(['PATCH'])
@firebase_authenticated
@is_owner(param_name="client_uuid", use_uuid=True)
def modifier_avis(request, avis_id):
    """
    Modifie un avis existant
    Seul le propriétaire de l'avis peut le modifier
    """
    try:
        # Récupérer le client connecté
        client = get_object_or_404(TblClient, idTblUser__uuid=request.user.uuid)

        # Récupérer l'avis et vérifier qu'il appartient au client
        avis = get_object_or_404(TblAvis, id=avis_id, client=client)

        # Seuls la note et le commentaire peuvent être modifiés
        data = {
            'note': request.data.get('note', avis.note),
            'commentaire': request.data.get('commentaire', avis.commentaire)
        }

        # Validation basique
        if 'note' in request.data:
            if not (1 <= int(data['note']) <= 5):
                return Response({
                    "success": False,
                    "message": "La note doit être entre 1 et 5"
                }, status=status.HTTP_400_BAD_REQUEST)

        if 'commentaire' in request.data:
            if len(data['commentaire'].strip()) < 10:
                return Response({
                    "success": False,
                    "message": "Le commentaire doit contenir au moins 10 caractères"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Mettre à jour l'avis
        avis.note = data['note']
        avis.commentaire = data['commentaire'].strip()
        avis.save()

        # Retourner l'avis modifié
        serializer = AvisDetailSerializer(avis)

        return Response({
            "success": True,
            "message": "Avis modifié avec succès",
            "avis": serializer.data
        })

    except TblAvis.DoesNotExist:
        return Response({
            "success": False,
            "message": "Avis non trouvé ou non autorisé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans modifier_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur lors de la modification: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 5️⃣ VIEW POUR SUPPRIMER UN AVIS
@api_view(['DELETE'])
@firebase_authenticated
@is_owner(param_name="client_uuid", use_uuid=True)
def supprimer_avis(request, avis_id):
    """
    Supprime un avis existant
    Seul le propriétaire de l'avis peut le supprimer
    """
    try:
        # Récupérer le client connecté
        client = get_object_or_404(TblClient, idTblUser__uuid=request.user.uuid)

        # Récupérer l'avis et vérifier qu'il appartient au client
        avis = get_object_or_404(TblAvis, id=avis_id, client=client)

        # Sauvegarder les infos avant suppression
        rdv_id = avis.rendez_vous.idRendezVous if avis.rendez_vous else None
        salon_nom = avis.salon.nom_salon

        # Supprimer l'avis
        avis.delete()

        return Response({
            "success": True,
            "message": f"Avis supprimé avec succès (RDV #{rdv_id} - {salon_nom})"
        })

    except TblAvis.DoesNotExist:
        return Response({
            "success": False,
            "message": "Avis non trouvé ou non autorisé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans supprimer_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur lors de la suppression: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 6️⃣ VIEW PUBLIQUE POUR LES AVIS D'UN SALON
@api_view(['GET'])
def avis_salon_public(request, salon_id):
    """
    API publique pour afficher les avis d'un salon
    Accessible sans authentification
    """
    try:
        salon = get_object_or_404(TblSalon, idTblSalon=salon_id)

        # Récupérer seulement les avis visibles
        avis = TblAvis.objects.filter(
            salon=salon,
            statut__code='visible'
        ).order_by('-date')

        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        avis_paginated = avis[start:end]
        serializer = AvisListSerializer(avis_paginated, many=True)

        # Statistiques
        stats = avis.aggregate(
            moyenne_notes=Avg('note'),
            total_avis=Count('id')
        )

        # Répartition par note
        repartition = {}
        for i in range(1, 6):
            repartition[f'note_{i}'] = avis.filter(note=i).count()

        return Response({
            "success": True,
            "salon": {
                "id": salon.idTblSalon,
                "nom": salon.nom_salon,
                "logo": salon.logo_salon.url if salon.logo_salon else None
            },
            "avis": serializer.data,
            "statistiques": {
                **stats,
                **repartition
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": avis.count(),
                "has_next": end < avis.count()
            }
        })

    except TblSalon.DoesNotExist:
        return Response({
            "success": False,
            "message": "Salon non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans avis_salon_public: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@firebase_authenticated
@is_admin
def admin_lister_avis(request):
    """
    Lister tous les avis pour modération admin
    Avec filtres et pagination
    """
    try:
        # Paramètres de filtrage
        statut_filter = request.GET.get('statut', '')  # visible, masque, etc.
        salon_filter = request.GET.get('salon_id', '')
        note_filter = request.GET.get('note', '')
        search = request.GET.get('search', '')  # Recherche dans commentaire ou nom client

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # Base query
        avis_queryset = TblAvis.objects.select_related(
            'client__idTblUser', 'salon', 'statut', 'rendez_vous'
        ).order_by('-date')

        # Filtres
        if statut_filter:
            avis_queryset = avis_queryset.filter(statut__code=statut_filter)

        if salon_filter:
            avis_queryset = avis_queryset.filter(salon__idTblSalon=salon_filter)

        if note_filter:
            avis_queryset = avis_queryset.filter(note=note_filter)

        if search:
            avis_queryset = avis_queryset.filter(
                Q(commentaire__icontains=search) |
                Q(client__idTblUser__nom__icontains=search) |
                Q(client__idTblUser__prenom__icontains=search) |
                Q(salon__nom_salon__icontains=search)
            )

        # Pagination
        total = avis_queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        avis_paginated = avis_queryset[start:end]

        # Sérialisation
        serializer = AdminAvisSerializer(avis_paginated, many=True)

        return Response({
            "success": True,
            "message": f"{total} avis trouvés",
            "avis": serializer.data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_next": end < total,
                "has_previous": page > 1
            }
        })

    except Exception as e:
        logger.error(f"Erreur dans admin_lister_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@firebase_authenticated
@is_admin
def admin_supprimer_avis(request, avis_id):
    """
    Supprimer un avis - Action admin
    """
    try:
        # Récupérer l'avis
        avis = get_object_or_404(TblAvis, id=avis_id)

        # Sauvegarder les infos pour le log
        client_nom = f"{avis.client.idTblUser.prenom} {avis.client.idTblUser.nom}"
        salon_nom = avis.salon.nom_salon
        admin_nom = f"{request.admin_user.prenom} {request.admin_user.nom}"

        # Supprimer l'avis
        avis.delete()

        logger.info(f"Admin {admin_nom} a supprimé l'avis de {client_nom} pour {salon_nom}")

        return Response({
            "success": True,
            "message": f"Avis de {client_nom} supprimé avec succès"
        })

    except TblAvis.DoesNotExist:
        return Response({
            "success": False,
            "message": "Avis non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Erreur dans admin_supprimer_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur lors de la suppression: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@firebase_authenticated
@is_admin
def admin_masquer_avis(request, avis_id):
    """
    Masquer/Démasquer un avis - Action admin
    """
    try:
        # Récupérer l'avis
        avis = get_object_or_404(TblAvis, id=avis_id)

        # Récupérer l'action demandée
        action = request.data.get('action', 'masquer')  # masquer ou visible

        if action not in ['masquer', 'visible']:
            return Response({
                "success": False,
                "message": "Action invalide. Utilisez 'masquer' ou 'visible'"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer le statut correspondant
        statut = get_object_or_404(TblAvisStatut, code=action)

        # Mettre à jour le statut
        ancien_statut = avis.statut.libelle
        avis.statut = statut
        avis.save()

        # Log
        client_nom = f"{avis.client.idTblUser.prenom} {avis.client.idTblUser.nom}"
        admin_nom = f"{request.admin_user.prenom} {request.admin_user.nom}"
        logger.info(
            f"Admin {admin_nom} a changé le statut de l'avis de {client_nom}: {ancien_statut} → {statut.libelle}")

        return Response({
            "success": True,
            "message": f"Avis {statut.libelle.lower()} avec succès",
            "nouveau_statut": {
                "code": statut.code,
                "libelle": statut.libelle
            }
        })

    except TblAvis.DoesNotExist:
        return Response({
            "success": False,
            "message": "Avis non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except TblAvisStatut.DoesNotExist:
        return Response({
            "success": False,
            "message": "Statut invalide"
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans admin_masquer_avis: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur lors de la modification: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@firebase_authenticated
@is_owner_coiffeuse
def avis_clients_coiffeuse(request):
    """
    Récupère tous les avis des clients pour la coiffeuse connectée
    Accessible uniquement aux coiffeuses propriétaires
    """
    try:
        # Récupérer la coiffeuse connectée
        user = request.user
        coiffeuse = get_object_or_404(TblCoiffeuse, idTblUser__uuid=user.uuid)

        # Récupérer le salon de la coiffeuse
        relation_salon = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse).first()

        if not relation_salon:
            return Response({
                "success": False,
                "message": "Aucun salon trouvé pour cette coiffeuse"
            }, status=status.HTTP_404_NOT_FOUND)

        salon = relation_salon.salon

        # Récupérer tous les avis du salon (visibles uniquement)
        # avis_queryset = TblAvis.objects.filter(
        #     salon=salon,
        #     statut__code='visible'  # Seulement les avis visibles
        # ).select_related(
        avis_queryset = TblAvis.objects.filter(
            salon=salon,
            statut__code='visible'  # Seulement les avis visibles
        ).select_related(
            'client__idTblUser',
            'rendez_vous',
            'statut'
        ).order_by('-date')

        # Paramètres de filtrage optionnels
        note_filter = request.GET.get('note', '')
        if note_filter:
            avis_queryset = avis_queryset.filter(note=note_filter)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size

        total = avis_queryset.count()
        avis_paginated = avis_queryset[start:end]

        # Sérialisation avec les détails clients
        serializer = CoiffeuseAvisClientSerializer(avis_paginated, many=True)

        return Response({
            "success": True,
            "message": f"{total} avis trouvés pour votre salon",
            "salon": {
                "id": salon.idTblSalon,
                "nom": salon.nom_salon
            },
            "avis": serializer.data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_next": end < total,
                "has_previous": page > 1
            }
        })

    except Exception as e:
        logger.error(f"Erreur dans avis_clients_coiffeuse: {str(e)}")
        return Response({
            "success": False,
            "message": f"Erreur interne: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)