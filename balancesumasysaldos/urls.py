# Archivo: balancesumasysaldos/urls.py
# Descripción: Define las rutas URL para el módulo de Balance de Sumas y Saldos.
# Incluye rutas para generar, visualizar y gestionar reportes contables.

from django.urls import path
from . import views

app_name = 'balancesumasysaldos'

urlpatterns = [
    # Rutas principales de balances
    path('', views.ListaBalancesView.as_view(), name='lista_balances'),
    path('crear/', views.CrearBalanceView.as_view(), name='crear_balance'),
    path('detalle/<int:pk>/', views.DetalleBalanceView.as_view(), name='detalle_balance'),
    
    # Rutas de gestión
    path('configuraciones/', views.gestionar_configuraciones, name='gestionar_configuraciones'),
    path('comparar/', views.comparar_balances, name='comparar_balances'),
    path('comparar/<int:pk1>/<int:pk2>/', views.resultado_comparacion, name='resultado_comparacion'),
    
    # Rutas de exportación
    path('exportar/<int:pk>/', views.exportar_balance, name='exportar_balance'),
]
