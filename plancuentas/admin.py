# Archivo: plancuentas/admin.py
# Descripción: Configuración del panel de administración para el Plan de Cuentas.
# Permite gestionar cuentas contables y saldos iniciales desde el admin de Django.

from django.contrib import admin
from django.utils.html import format_html
from .models import PlanCuentas, SaldoInicial

@admin.register(PlanCuentas)
class PlanCuentasAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para PlanCuentas.
    Incluye filtros, búsqueda y visualización jerárquica.
    """
    list_display = [
        'codigo', 'nombre', 'tipo', 'naturaleza', 'nivel', 
        'cuenta_padre', 'activa', 'permite_movimiento', 'fecha_creacion'
    ]
    list_filter = [
        'tipo', 'naturaleza', 'nivel', 'activa', 'permite_movimiento', 
        'fecha_creacion', 'fecha_modificacion'
    ]
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('tipo', 'naturaleza', 'nivel')
        }),
        ('Jerarquía', {
            'fields': ('cuenta_padre',)
        }),
        ('Configuración', {
            'fields': ('activa', 'permite_movimiento')
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('cuenta_padre')
    
    def get_list_display(self, request):
        """
        Personalizar la visualización según el usuario.
        """
        list_display = list(super().get_list_display(request))
        return list_display

@admin.register(SaldoInicial)
class SaldoInicialAdmin(admin.ModelAdmin):
    """
    Configuración del admin para SaldoInicial.
    Permite gestionar los saldos iniciales de las cuentas.
    """
    list_display = [
        'cuenta', 'saldo', 'fecha', 'observaciones', 'fecha_creacion'
    ]
    list_filter = ['fecha', 'fecha_creacion']
    search_fields = ['cuenta__codigo', 'cuenta__nombre', 'observaciones']
    ordering = ['cuenta__codigo', 'fecha']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Saldo', {
            'fields': ('cuenta', 'saldo', 'fecha')
        }),
        ('Detalles', {
            'fields': ('observaciones',)
        }),
    )
    
    readonly_fields = ['fecha_creacion']
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('cuenta')
