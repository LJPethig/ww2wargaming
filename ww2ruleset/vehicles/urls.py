from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('vehicles/', views.browse_view, name='browse'),
    path('vehicles/grid/', views.vehicle_grid_view, name='vehicle_grid'),
    path('vehicles/<int:pk>/', views.vehicle_detail_view, name='vehicle_detail'),
]