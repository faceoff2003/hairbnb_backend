from django.urls import path

from hairbnb.coiffeuse.coiffeuse_views import get_coiffeuses_info, update_coiffeuse_nom_commercial

urlpatterns = [
    path('get_coiffeuses_info/', get_coiffeuses_info, name="get_coiffeuses_info"),
    path('update-nom-commercial/<str:uuid>/', update_coiffeuse_nom_commercial, name='update_coiffeuse_nom_commercial'),

]