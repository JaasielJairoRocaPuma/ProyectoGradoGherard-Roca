# Archivo: plancuentas/urls.py
# Descripción: Define las rutas URL para el módulo de Plan de Cuentas.
# Incluye rutas para CRUD de cuentas, búsqueda y gestión de saldos.

from django.urls import path
from . import views

app_name = 'comprobantes'

urlpatterns = [
    # Rutas principales del Plan de Cuentas
    path('', views.lista_comprobantes, name='lista_comprobantes'),
    path('<int:id>/', views.detalle_comprobante, name='detalle_comprobante'),
    path('obtener-ufv-gpt/', views.obtener_ufv_gpt, name='obtener_ufv_gpt'),
    path('insertar/', views.insertar_comprobante, name='insertar'),
]