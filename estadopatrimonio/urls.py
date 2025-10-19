# Archivo: estadopatrimonio/urls.py
# Descripción: Define las rutas URL para el módulo de Estado Patrimonial.
# Incluye rutas para generar, visualizar y gestionar estados financieros.

from django.urls import path
from . import views

app_name = 'estadopatrimonio'

urlpatterns = [
    # Rutas principales de estados patrimoniales
    path('patrimoniales/', views.ListaEstadosPatrimonialesView.as_view(), name='lista_estados_patrimoniales'),
    path('patrimoniales/crear/', views.CrearEstadoPatrimonialView.as_view(), name='crear_estado_patrimonial'),
    path('patrimoniales/detalle/<int:pk>/', views.DetalleEstadoPatrimonialView.as_view(), name='detalle_estado_patrimonial'),
    
    # Rutas principales de estados de resultados
    path('resultados/', views.ListaEstadosResultadosView.as_view(), name='lista_estados_resultados'),
    path('resultados/crear/', views.CrearEstadoResultadosView.as_view(), name='crear_estado_resultados'),
    path('resultados/detalle/<int:pk>/', views.DetalleEstadoResultadosView.as_view(), name='detalle_estado_resultados'),
    
    # Rutas de gestión
    path('configuraciones/', views.gestionar_configuraciones, name='gestionar_configuraciones'),
    path('comparar/', views.comparar_estados, name='comparar_estados'),
    path('comparar/<str:tipo>/<int:pk1>/<int:pk2>/', views.resultado_comparacion, name='resultado_comparacion'),
    
    # Rutas de análisis
    path('analisis/', views.analisis_financiero, name='analisis_financiero'),
    path('analisis/<str:tipo>/<str:desde>/<str:hasta>/', views.resultado_analisis, name='resultado_analisis'),
    
    # Rutas de exportación
    path('exportar/<str:tipo>/<int:pk>/', views.exportar_estado, name='exportar_estado'),
]
