# Archivo: plancuentas/urls.py
# Descripción: Define las rutas URL para el módulo de Plan de Cuentas.
# Incluye rutas para CRUD de cuentas, búsqueda y gestión de saldos.

from django.urls import path
from . import views

app_name = 'plancuentas'

urlpatterns = [
    # Rutas principales del Plan de Cuentas
    path('', views.ListaPlanCuentasView, name='lista_cuentas'),
    path('imprimirexcel/', views.reporte_excel, name='imprimirexcel'),
    path('imprimirpdf/', views.reporte_pdf, name='imprimirpdf'),
    # path('crear/', views.CrearCuentaView.as_view(), name='crear_cuenta'),
    # path('editar/<int:pk>/', views.EditarCuentaView.as_view(), name='editar_cuenta'),
    # path('eliminar/<int:pk>/', views.EliminarCuentaView.as_view(), name='eliminar_cuenta'),
    # path('detalle/<int:pk>/', views.detalle_cuenta, name='detalle_cuenta'),
    
    # # Rutas de visualización
    # path('arbol/', views.arbol_cuentas, name='arbol_cuentas'),
    
    # # Rutas de gestión de saldos
    # path('saldos-iniciales/', views.gestionar_saldos_iniciales, name='gestionar_saldos'),
    
    # # Rutas AJAX
    # path('buscar-ajax/', views.buscar_cuenta_ajax, name='buscar_cuenta_ajax'),
    
    # # Rutas de exportación
    # path('exportar/', views.exportar_plan_cuentas, name='exportar_plan_cuentas'),
]
