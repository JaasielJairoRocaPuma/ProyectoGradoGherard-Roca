from django.contrib import admin
from .models import Comprobante, Firmas, DescripcionCuentas

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'glosa', 'beneficiario', 'tipocambio', 'ufv', 'tipo','imagen')
    search_fields = ('numero', 'glosa', 'beneficiario')
    
@admin.register(Firmas)
class FirmasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cargo', 'ci', 'extencion')
    search_fields = ('nombre', 'ci')
@admin.register(DescripcionCuentas)
class DescripcionCuentasAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'debe', 'haber')
    search_fields = ('cuenta__codigo', 'cuenta__nombre')