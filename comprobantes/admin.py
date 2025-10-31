# Archivo: comprobantes/admin.py
# Descripción: Configuración del panel de administración para el módulo de comprobantes.
# Permite gestionar comprobantes, detalles y secuencias desde el admin de Django.

from django.contrib import admin
from django.utils.html import format_html
from .models import Comprobante, DetalleComprobante, SecuenciaComprobante

class DetalleComprobanteInline(admin.TabularInline):
    """
    Inline para mostrar detalles de comprobantes en el admin.
    Permite editar detalles directamente desde el comprobante.
    """
    model = DetalleComprobante
    extra = 1
    fields = ['cuenta', 'concepto', 'debe', 'haber', 'orden']
    readonly_fields = []

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para Comprobante.
    Incluye filtros, búsqueda y visualización de detalles.
    """
    list_display = [
        'numero', 'tipo', 'fecha', 'concepto', 'estado', 
        'total_debe', 'total_haber', 'usuario_creacion', 'fecha_creacion'
    ]
    list_filter = [
        'tipo', 'estado', 'fecha', 'fecha_creacion', 
        'usuario_creacion', 'usuario_aprobacion'
    ]
    search_fields = ['numero', 'concepto', 'referencia']
    ordering = ['-fecha', '-numero']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'tipo', 'fecha', 'concepto')
        }),
        ('Detalles', {
            'fields': ('referencia', 'observaciones')
        }),
        ('Estado y Totales', {
            'fields': ('estado', 'total_debe', 'total_haber')
        }),
        ('Auditoría', {
            'fields': ('usuario_creacion', 'usuario_aprobacion', 'fecha_creacion', 'fecha_aprobacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'numero', 'total_debe', 'total_haber', 'fecha_creacion', 
        'fecha_modificacion', 'fecha_aprobacion'
    ]
    
    inlines = [DetalleComprobanteInline]
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related(
            'usuario_creacion', 'usuario_aprobacion'
        )

@admin.register(DetalleComprobante)
class DetalleComprobanteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DetalleComprobante.
    Permite gestionar los detalles de comprobantes.
    """
    list_display = [
        'comprobante', 'cuenta', 'concepto', 'debe', 'haber', 'orden'
    ]
    list_filter = ['comprobante__tipo', 'comprobante__fecha', 'cuenta__tipo']
    search_fields = [
        'comprobante__numero', 'cuenta__codigo', 'cuenta__nombre', 'concepto'
    ]
    ordering = ['comprobante', 'orden']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('comprobante', 'cuenta', 'concepto')
        }),
        ('Valores', {
            'fields': ('debe', 'haber', 'orden')
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related.
        """
        return super().get_queryset(request).select_related(
            'comprobante', 'cuenta'
        )

@admin.register(SecuenciaComprobante)
class SecuenciaComprobanteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para SecuenciaComprobante.
    Permite gestionar las secuencias de numeración.
    """
    list_display = [
        'tipo', 'prefijo', 'siguiente_numero', 'formato', 'activo'
    ]
    list_filter = ['tipo', 'activo']
    search_fields = ['tipo', 'prefijo']
    ordering = ['tipo']
    
    fieldsets = (
        ('Configuración de Secuencia', {
            'fields': ('tipo', 'prefijo', 'formato')
        }),
        ('Control de Numeración', {
            'fields': ('siguiente_numero', 'activo')
        }),
    )
    
    readonly_fields = ['siguiente_numero']
