# Archivo: comprobantes/urls.py
# Descripción: Define las rutas URL para el módulo de comprobantes contables.
# Incluye rutas para CRUD de comprobantes, aprobación y gestión de secuencias.

from django.urls import path
from . import views

app_name = 'comprobantes'

urlpatterns = [
    # Rutas principales de comprobantes
    path('', views.ListaComprobantesView.as_view(), name='lista_comprobantes'),
    path('crear/', views.CrearComprobanteView.as_view(), name='crear_comprobante'),
    path('editar/<int:pk>/', views.EditarComprobanteView.as_view(), name='editar_comprobante'),
    path('detalle/<int:pk>/', views.DetalleComprobanteView.as_view(), name='detalle_comprobante'),
    
    # Rutas de gestión de comprobantes
    path('aprobar/<int:pk>/', views.aprobar_comprobante, name='aprobar_comprobante'),
    path('anular/<int:pk>/', views.anular_comprobante, name='anular_comprobante'),
    
    # Rutas de configuración
    path('secuencias/', views.gestionar_secuencias, name='gestionar_secuencias'),
    
    # Rutas AJAX
    path('buscar-cuenta-ajax/', views.buscar_cuenta_ajax, name='buscar_cuenta_ajax'),
    
    # Rutas de reportes
    path('reportes/', views.reporte_comprobantes, name='reporte_comprobantes'),
]
