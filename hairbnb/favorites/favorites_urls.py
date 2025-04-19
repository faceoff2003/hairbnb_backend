from django.urls import path

from hairbnb.favorites.favorites_views import get_favorites, add_favorite, remove_favorite

urlpatterns = [
    path('favorites/', get_favorites),
    path('favorites/add/', add_favorite),
    path('favorites/remove/<int:salon_id>/', remove_favorite),

]