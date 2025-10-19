# Archivo: balancesumasysaldos/admin.py
# Descripción: Configuración del panel de administración para el Balance de Sumas y Saldos.
# Permite gestionar balances, detalles y configuraciones desde el admin de Django.

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BalanceSumasSaldos, DetalleBalance, ConfiguracionBalance, ResumenBalance
)

class DetalleBalanceInline(admin.TabularInline):
    """
    Inline para mostrar detalles de balance en el admin.
    Permite ver detalles directamente desde el balance.
    """
    model = DetalleBalance
    extra = 0
    fields = ['cuenta', 'saldo_anterior', 'movimientos_debe', 'movimientos_haber', 
              'saldo_debe', 'saldo_haber', 'saldo_final', 'orden']
    readonly_fields = ['saldo_final']
    ordering = ['orden']

class ResumenBalanceInline(admin.TabularInline):
    """
    Inline para mostrar resúmenes de balance en el admin.
    """
    model = ResumenBalance
    extra = 0
    fields = ['tipo_cuenta', 'total_debe', 'total_haber', 'saldo_neto', 'cantidad_cuentas']
    readonly_fields = ['saldo_neto']

@admin.register(BalanceSumasSaldos)
class BalanceSumasSaldosAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para BalanceSumasSaldos.
    Incluye filtros, búsqueda y visualización de detalles.
    """
    list_display = [
        'nombre', 'fecha_desde', 'fecha_hasta', 'usuario_generacion', 
        'fecha_generacion', 'incluir_saldos_cero', 'solo_cuentas_movimiento'
    ]
    list_filter = [
        'fecha_desde', 'fecha_hasta', 'fecha_generacion', 
        'usuario_generacion', 'incluir_saldos_cero', 'solo_cuentas_movimiento'
    ]
    search_fields = ['nombre', 'observaciones']
    ordering = ['-fecha_generacion']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'fecha_desde', 'fecha_hasta')
        }),
        ('Configuración', {
            'fields': ('incluir_saldos_cero', 'solo_cuentas_movimiento')
        }),
        ('Detalles', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('usuario_generacion', 'fecha_generacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_generacion']
    
    inlines = [DetalleBalanceInline, ResumenBalanceInline]
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('usuario_generacion')

@admin.register(DetalleBalance)
class DetalleBalanceAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DetalleBalance.
    Permite gestionar los detalles de balances.
    """
    list_display = [
        'balance', 'cuenta', 'saldo_anterior', 'movimientos_debe', 
        'movimientos_haber', 'saldo_debe', 'saldo_haber', 'saldo_final'
    ]
    list_filter = [
        'balance__fecha_desde', 'balance__fecha_hasta', 
        'cuenta__tipo', 'cuenta__naturaleza'
    ]
    search_fields = [
        'balance__nombre', 'cuenta__codigo', 'cuenta__nombre'
    ]
    ordering = ['balance', 'orden']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Balance', {
            'fields': ('balance', 'cuenta', 'orden')
        }),
        ('Saldos Anteriores', {
            'fields': ('saldo_anterior',)
        }),
        ('Movimientos del Período', {
            'fields': ('movimientos_debe', 'movimientos_haber')
        }),
        ('Saldos Finales', {
            'fields': ('saldo_debe', 'saldo_haber', 'saldo_final')
        }),
    )
    
    readonly_fields = ['saldo_final']
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related(
            'balance', 'cuenta'
        )

@admin.register(ConfiguracionBalance)
class ConfiguracionBalanceAdmin(admin.ModelAdmin):
    """
    Configuración del admin para ConfiguracionBalance.
    Permite gestionar las configuraciones de balance.
    """
    list_display = [
        'nombre', 'incluir_saldos_cero', 'solo_cuentas_movimiento',
        'agrupar_por_tipo', 'mostrar_saldos_anteriores', 'mostrar_movimientos',
        'formato_numero', 'activa'
    ]
    list_filter = [
        'incluir_saldos_cero', 'solo_cuentas_movimiento', 'agrupar_por_tipo',
        'mostrar_saldos_anteriores', 'mostrar_movimientos', 'activa'
    ]
    search_fields = ['nombre']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'activa')
        }),
        ('Opciones de Inclusión', {
            'fields': ('incluir_saldos_cero', 'solo_cuentas_movimiento')
        }),
        ('Opciones de Visualización', {
            'fields': ('agrupar_por_tipo', 'mostrar_saldos_anteriores', 'mostrar_movimientos')
        }),
        ('Formato', {
            'fields': ('formato_numero',)
        }),
    )

@admin.register(ResumenBalance)
class ResumenBalanceAdmin(admin.ModelAdmin):
    """
    Configuración del admin para ResumenBalance.
    Permite gestionar los resúmenes de balance.
    """
    list_display = [
        'balance', 'tipo_cuenta', 'total_debe', 'total_haber', 
        'saldo_neto', 'cantidad_cuentas'
    ]
    list_filter = [
        'balance__fecha_desde', 'balance__fecha_hasta', 'tipo_cuenta'
    ]
    search_fields = [
        'balance__nombre', 'tipo_cuenta'
    ]
    ordering = ['balance', 'tipo_cuenta']
    
    fieldsets = (
        ('Información del Balance', {
            'fields': ('balance', 'tipo_cuenta')
        }),
        ('Totales', {
            'fields': ('total_debe', 'total_haber', 'saldo_neto')
        }),
        ('Estadísticas', {
            'fields': ('cantidad_cuentas',)
        }),
    )
    
    readonly_fields = ['saldo_neto']
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('balance')
