# Archivo: estadopatrimonio/admin.py
# Descripción: Configuración del panel de administración para el Estado Patrimonial.
# Permite gestionar estados financieros y configuraciones desde el admin de Django.

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EstadoPatrimonial, EstadoResultados, ConfiguracionEstado,
    DetalleEstadoPatrimonial, DetalleEstadoResultados, ResumenFinanciero
)

class DetalleEstadoPatrimonialInline(admin.TabularInline):
    """
    Inline para mostrar detalles de estado patrimonial en el admin.
    """
    model = DetalleEstadoPatrimonial
    extra = 0
    fields = ['cuenta', 'saldo_final', 'orden']
    ordering = ['orden']

class DetalleEstadoResultadosInline(admin.TabularInline):
    """
    Inline para mostrar detalles de estado de resultados en el admin.
    """
    model = DetalleEstadoResultados
    extra = 0
    fields = ['cuenta', 'saldo_final', 'orden']
    ordering = ['orden']

class ResumenFinancieroInline(admin.TabularInline):
    """
    Inline para mostrar resúmenes financieros en el admin.
    """
    model = ResumenFinanciero
    extra = 0
    fields = ['total_activos', 'total_pasivos', 'total_patrimonio', 'ratio_liquidez', 'ratio_endeudamiento']
    readonly_fields = ['ratio_liquidez', 'ratio_endeudamiento']

@admin.register(EstadoPatrimonial)
class EstadoPatrimonialAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para EstadoPatrimonial.
    Incluye filtros, búsqueda y visualización de detalles.
    """
    list_display = [
        'nombre', 'fecha', 'usuario_generacion', 'fecha_generacion'
    ]
    list_filter = [
        'fecha', 'fecha_generacion', 'usuario_generacion'
    ]
    search_fields = ['nombre', 'observaciones']
    ordering = ['-fecha_generacion']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'fecha')
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
    
    inlines = [DetalleEstadoPatrimonialInline, ResumenFinancieroInline]
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('usuario_generacion')

@admin.register(EstadoResultados)
class EstadoResultadosAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para EstadoResultados.
    Incluye filtros, búsqueda y visualización de detalles.
    """
    list_display = [
        'nombre', 'fecha_desde', 'fecha_hasta', 'usuario_generacion', 'fecha_generacion'
    ]
    list_filter = [
        'fecha_desde', 'fecha_hasta', 'fecha_generacion', 'usuario_generacion'
    ]
    search_fields = ['nombre', 'observaciones']
    ordering = ['-fecha_generacion']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'fecha_desde', 'fecha_hasta')
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
    
    inlines = [DetalleEstadoResultadosInline]
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('usuario_generacion')

@admin.register(DetalleEstadoPatrimonial)
class DetalleEstadoPatrimonialAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DetalleEstadoPatrimonial.
    Permite gestionar los detalles de estados patrimoniales.
    """
    list_display = [
        'estado', 'cuenta', 'saldo_final', 'orden'
    ]
    list_filter = [
        'estado__fecha', 'cuenta__tipo', 'cuenta__naturaleza'
    ]
    search_fields = [
        'estado__nombre', 'cuenta__codigo', 'cuenta__nombre'
    ]
    ordering = ['estado', 'orden']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Estado', {
            'fields': ('estado', 'cuenta', 'orden')
        }),
        ('Valores', {
            'fields': ('saldo_final',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related(
            'estado', 'cuenta'
        )

@admin.register(DetalleEstadoResultados)
class DetalleEstadoResultadosAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DetalleEstadoResultados.
    Permite gestionar los detalles de estados de resultados.
    """
    list_display = [
        'estado', 'cuenta', 'saldo_final', 'orden'
    ]
    list_filter = [
        'estado__fecha_desde', 'estado__fecha_hasta', 'cuenta__tipo'
    ]
    search_fields = [
        'estado__nombre', 'cuenta__codigo', 'cuenta__nombre'
    ]
    ordering = ['estado', 'orden']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Estado', {
            'fields': ('estado', 'cuenta', 'orden')
        }),
        ('Valores', {
            'fields': ('saldo_final',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related(
            'estado', 'cuenta'
        )

@admin.register(ConfiguracionEstado)
class ConfiguracionEstadoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para ConfiguracionEstado.
    Permite gestionar las configuraciones de estados financieros.
    """
    list_display = [
        'nombre', 'incluir_saldos_cero', 'agrupar_por_tipo',
        'mostrar_cuentas_principales', 'formato_numero', 'activa'
    ]
    list_filter = [
        'incluir_saldos_cero', 'agrupar_por_tipo', 'mostrar_cuentas_principales', 'activa'
    ]
    search_fields = ['nombre']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'activa')
        }),
        ('Opciones de Inclusión', {
            'fields': ('incluir_saldos_cero',)
        }),
        ('Opciones de Visualización', {
            'fields': ('agrupar_por_tipo', 'mostrar_cuentas_principales')
        }),
        ('Formato', {
            'fields': ('formato_numero',)
        }),
    )

@admin.register(ResumenFinanciero)
class ResumenFinancieroAdmin(admin.ModelAdmin):
    """
    Configuración del admin para ResumenFinanciero.
    Permite gestionar los resúmenes financieros.
    """
    list_display = [
        'estado_patrimonial', 'total_activos', 'total_pasivos', 
        'total_patrimonio', 'ratio_liquidez', 'ratio_endeudamiento'
    ]
    list_filter = [
        'estado_patrimonial__fecha', 'estado_patrimonial__usuario_generacion'
    ]
    search_fields = [
        'estado_patrimonial__nombre'
    ]
    ordering = ['estado_patrimonial']
    
    fieldsets = (
        ('Información del Estado', {
            'fields': ('estado_patrimonial',)
        }),
        ('Totales', {
            'fields': ('total_activos', 'total_pasivos', 'total_patrimonio')
        }),
        ('Ratios Financieros', {
            'fields': ('ratio_liquidez', 'ratio_endeudamiento')
        }),
    )
    
    readonly_fields = ['ratio_liquidez', 'ratio_endeudamiento']
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related('estado_patrimonial')
