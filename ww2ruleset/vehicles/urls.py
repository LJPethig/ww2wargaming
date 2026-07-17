from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('vehicles/', views.nationality_list_view, name='nationality_list'),
    path('vehicles/<str:nationality>/', views.type_list_view, name='type_list'),
    path('vehicles/<str:nationality>/<str:vehicle_type>/', views.vehicle_list_view, name='vehicle_list'),
]