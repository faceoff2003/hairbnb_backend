from django.urls import path

from hairbnb.currentUser.currentUser_views import get_current_user
from hairbnb.favorites.favorites_views import get_favorites, add_favorite, remove_favorite, get_user_favorites

urlpatterns = [
    path('get_current_user/', get_current_user, name='get_current_user'),

]