# Archivo: plancuentas/admin.py
# Descripción: Configuración del panel de administración para el Plan de Cuentas.
# Permite gestionar cuentas contables y saldos iniciales desde el admin de Django.

from django.contrib import admin
from django.utils.html import format_html
from .models import Grupo, SubGrupo, CuentaMatriz, CuentaMayor, CuentaAuxiliar


# --- Configuración base para mostrar el código calculado ---
class CodigoMixin:
    """
    Mixin que agrega una columna 'Código' que llama al método codigo().
    """
    def mostrar_codigo(self, obj):
        return obj.codigo
    mostrar_codigo.short_description = "Código"


# --- ADMIN DE CADA MODELO ---

@admin.register(Grupo)
class GrupoAdmin(CodigoMixin, admin.ModelAdmin):
    list_display = ('mostrar_codigo', 'nombre', 'tipo', 'nivel')
    search_fields = ('nombre',)
    list_filter = ('tipo',)
    ordering = ('id',)


@admin.register(SubGrupo)
class SubGrupoAdmin(CodigoMixin, admin.ModelAdmin):
    list_display = ('mostrar_codigo', 'nombre', 'grupo', 'tipo', 'nivel')
    search_fields = ('nombre',)
    list_filter = ('tipo', 'grupo')
    ordering = ('grupo__id', 'cod')


@admin.register(CuentaMatriz)
class CuentaMatrizAdmin(CodigoMixin, admin.ModelAdmin):
    list_display = ('mostrar_codigo', 'nombre', 'subgrupo', 'tipo', 'nivel')
    search_fields = ('nombre',)
    list_filter = ('tipo', 'subgrupo__grupo')
    ordering = ('subgrupo__grupo__id', 'subgrupo__cod', 'cod')


@admin.register(CuentaMayor)
class CuentaMayorAdmin(CodigoMixin, admin.ModelAdmin):
    list_display = ('mostrar_codigo', 'nombre', 'cuentamatriz', 'tipo', 'nivel')
    search_fields = ('nombre',)
    list_filter = ('tipo', 'cuentamatriz__subgrupo__grupo')
    ordering = ('cuentamatriz__subgrupo__grupo__id', 'cuentamatriz__subgrupo__cod', 'cuentamatriz__cod', 'cod')


@admin.register(CuentaAuxiliar)
class CuentaAuxiliarAdmin(CodigoMixin, admin.ModelAdmin):
    list_display = ('mostrar_codigo', 'nombre', 'cuentamayor', 'tipo', 'nivel')
    search_fields = ('nombre',)
    list_filter = ('tipo', 'cuentamayor__cuentamatriz__subgrupo__grupo')
    ordering = (
        'cuentamayor__cuentamatriz__subgrupo__grupo__id',
        'cuentamayor__cuentamatriz__subgrupo__cod',
        'cuentamayor__cuentamatriz__cod',
        'cuentamayor__cod',
        'cod'
    )
