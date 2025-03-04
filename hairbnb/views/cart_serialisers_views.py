from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from hairbnb.business.business_logic import CartData, CartItemData
from hairbnb.models import TblCart, TblCartItem, TblService, TblUser

# 🛒 **Récupérer le panier d'un utilisateur spécifique**
# @api_view(['GET'])
# def get_cart(request, user_id):
#     """
#     Récupérer le panier d'un utilisateur via son ID.
#     """
#     user = get_object_or_404(TblUser, idTblUser=user_id)  # Vérifie si l'utilisateur existe
#     cart, created = TblCart.objects.get_or_create(user=user)  # Récupère ou crée le panier
#
#     return Response(CartData(cart).to_dict(), status=200)

@api_view(['GET'])
def get_cart(request, user_id):
    try:
        user = TblUser.objects.get(idTblUser=user_id)  # Vérifie l'utilisateur
        cart, created = TblCart.objects.get_or_create(user=user)  # Récupère ou crée le panier

        if not cart.items.exists():
            return Response({"items": [], "coiffeuse_id": None}, status=200)

        # ✅ Correction : Récupérer la coiffeuse via la table de liaison
        first_service = cart.items.first().service
        first_salon_service = first_service.salon_service.first()  # Prend la première relation
        coiffeuse_id = first_salon_service.salon.coiffeuse.idTblUser.idTblUser if first_salon_service else None

        return Response({
            "items": [CartItemData(item).to_dict() for item in cart.items.all()],  # ✅ Inclut maintenant la promo
            "coiffeuse_id": coiffeuse_id
        }, status=200)

    except TblUser.DoesNotExist:
        return Response({"error": "Utilisateur introuvable"}, status=404)

    except Exception as e:
        return Response({"error": f"Erreur interne : {str(e)}"}, status=500)



# @api_view(['GET'])
# def get_cart(request, user_id):
#     try:
#         user = TblUser.objects.get(idTblUser=user_id)  # Vérifie l'utilisateur
#         cart, created = TblCart.objects.get_or_create(user=user)  # Récupère ou crée le panier
#
#         if not cart.items.exists():
#             return Response({"items": [], "coiffeuse_id": None}, status=200)
#
#         # ✅ Correction : Récupérer la coiffeuse via la table de liaison
#         first_service = cart.items.first().service
#         first_salon_service = first_service.salon_service.first()  # Prend la première relation
#         coiffeuse_id = first_salon_service.salon.coiffeuse.idTblUser.idTblUser if first_salon_service else None
#
#         return Response({
#             "items": [CartItemData(item).to_dict() for item in cart.items.all()],
#             "coiffeuse_id": coiffeuse_id
#         }, status=200)
#
#     except TblUser.DoesNotExist:
#         return Response({"error": "Utilisateur introuvable"}, status=404)
#
#     except Exception as e:
#         return Response({"error": f"Erreur interne : {str(e)}"}, status=500)




# ➕ **Ajouter un service au panier**
@api_view(['POST'])
def add_to_cart(request):
    """
    Ajouter un service au panier via l'ID utilisateur et l'ID service.
    """
    user_id = request.data.get('user_id')  # Récupère l'ID utilisateur envoyé dans la requête
    service_id = request.data.get('service_id')
    quantity = int(request.data.get('quantity', 1))

    user = get_object_or_404(TblUser, idTblUser=user_id)  # Vérifie si l'utilisateur existe
    service = get_object_or_404(TblService, idTblService=service_id)  # Vérifie si le service existe

    cart, created = TblCart.objects.get_or_create(user=user)  # Récupère ou crée le panier

    # Vérifier si le service est déjà dans le panier
    cart_item, created = TblCartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        cart_item.quantity += quantity  # Incrémente si déjà présent
    cart_item.save()

    return Response({"message": "Service ajouté au panier ✅", "cart": CartData(cart).to_dict()}, status=200)


# ❌ **Supprimer un service du panier**
@api_view(['DELETE'])
def remove_from_cart(request):
    """
    Supprime un service du panier d'un utilisateur spécifique.
    """
    user_id = request.data.get('user_id')  # Récupère l'ID utilisateur
    service_id = request.data.get('service_id')  # Récupère l'ID du service

    user = get_object_or_404(TblUser, idTblUser=user_id)
    cart = get_object_or_404(TblCart, user=user)  # Récupère le panier de l'utilisateur
    cart_item = get_object_or_404(TblCartItem, cart=cart, service_id=service_id)  # Récupère l'élément à supprimer

    cart_item.delete()  # Supprime l'article du panier

    return Response({"message": "Service supprimé du panier ✅", "cart": CartData(cart).to_dict()}, status=200)


# 🗑 **Vider complètement le panier d'un utilisateur**
@api_view(['DELETE'])
def clear_cart(request):
    """
    Vide le panier d'un utilisateur via son ID.
    """
    user_id = request.data.get('user_id')  # Récupère l'ID utilisateur

    user = get_object_or_404(TblUser, idTblUser=user_id)
    cart = get_object_or_404(TblCart, user=user)
    cart.items.all().delete()  # Supprime tous les articles du panier

    return Response({"message": "Panier vidé ✅", "cart": CartData(cart).to_dict()}, status=200)










#from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import get_object_or_404
# from hairbnb.business.business_logic import CartData
# from hairbnb.models import TblCart, TblCartItem, TblService
#
# # 🛒 **Récupérer le panier de l'utilisateur connecté**
# @api_view(['GET'])
# #@permission_classes([IsAuthenticated])
# def get_cart(request):
#     cart, created = TblCart.objects.get_or_create(user=request.user)
#     return Response(CartData(cart).to_dict(), status=200)
#
# # ➕ **Ajouter un service au panier**
# @api_view(['POST'])
# #@permission_classes([IsAuthenticated])
# def add_to_cart(request):
#     user = request.user
#     service_id = request.data.get('service_id')
#     quantity = int(request.data.get('quantity', 1))
#
#     # Vérifier que le service existe
#     service = get_object_or_404(TblService, idTblService=service_id)
#
#     # Récupérer ou créer le panier
#     cart, created = TblCart.objects.get_or_create(user=user)
#
#     # Vérifier si l'article est déjà dans le panier
#     cart_item, created = TblCartItem.objects.get_or_create(cart=cart, service=service)
#     if not created:
#         cart_item.quantity += quantity  # Incrémente si déjà présent
#     cart_item.save()
#
#     return Response({"message": "Service ajouté au panier !", "cart": CartData(cart).to_dict()}, status=200)
#
# # ❌ **Supprimer un service du panier**
# @api_view(['DELETE'])
# #@permission_classes([IsAuthenticated])
# def remove_from_cart(request):
#     user = request.user
#     service_id = request.data.get('service_id')
#
#     cart = get_object_or_404(TblCart, user=user)
#     cart_item = get_object_or_404(TblCartItem, cart=cart, service_id=service_id)
#     cart_item.delete()
#
#     return Response({"message": "Service supprimé du panier !", "cart": CartData(cart).to_dict()}, status=200)
#
# # 🗑 **Vider le panier**
# @api_view(['DELETE'])
# #@permission_classes([IsAuthenticated])
# def clear_cart(request):
#     user = request.user
#     cart = get_object_or_404(TblCart, user=user)
#     cart.items.all().delete()  # Supprime tous les articles du panier
#
#     return Response({"message": "Panier vidé !", "cart": CartData(cart).to_dict()}, status=200)
