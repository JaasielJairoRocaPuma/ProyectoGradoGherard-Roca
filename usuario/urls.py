# Archivo: usuario/urls.py
# Descripción: Define las rutas URL para el módulo de usuario del sistema contable.
# Incluye rutas para login, logout, dashboard y gestión de perfil.

from django.urls import path
from . import views

app_name = 'usuario'

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Rutas del dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Rutas de perfil de usuario
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # Rutas AJAX
    path('verificar-sesion/', views.verificar_sesion, name='verificar_sesion'),
    path('datos-grafico-cuentas/', views.datos_grafico_cuentas, name='datos_grafico_cuentas'),
    path('alertas-cuentas-rojo/', views.alertas_cuentas_rojo, name='alertas_cuentas_rojo'),
]
