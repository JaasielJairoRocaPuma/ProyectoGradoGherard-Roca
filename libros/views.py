from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from comprobantes.models import Comprobante, TipoComprobante, DescripcionCuentas
from plancuentas.models import CuentaAuxiliar
from django.db.models import Sum, Q
from collections import defaultdict

# Create your views here.

@login_required
def lista_libros(request):
    """
    Vista que muestra la lista de libros mayores por tipo de comprobante.
    Cada tipo de comprobante es un libro mayor.
    """
    tipos_comprobante = TipoComprobante.choices
    
    # Obtener estadísticas por tipo
    libros_info = []
    for tipo_valor, tipo_nombre in tipos_comprobante:
        comprobantes = Comprobante.objects.filter(tipo=tipo_valor).order_by('numero')
        total_comprobantes = comprobantes.count()
        
        libros_info.append({
            'tipo': tipo_valor,
            'nombre': tipo_nombre,
            'total_comprobantes': total_comprobantes,
            'comprobantes': comprobantes[:5]  # Primeros 5 para preview
        })
    
    return render(request, 'libros/lista_libros.html', {
        'libros_info': libros_info
    })

@login_required
def detalle_libro(request, tipo):
    """
    Vista que muestra el libro mayor detallado de un tipo de comprobante.
    Muestra los comprobantes organizados por tipo de cuenta de nivel 5 (subsecciones).
    """
    tipo_nombre = dict(TipoComprobante.choices).get(tipo, 'Desconocido')
    comprobantes = Comprobante.objects.filter(tipo=tipo).order_by('numero')
    
    # Preparar datos de cada comprobante para el template, agrupados por tipo de cuenta
    comprobantes_por_seccion = defaultdict(lambda: defaultdict(list))
    
    for comp in comprobantes:
        for desc_cuenta in comp.descripcionCuentas.all():
            tipo_cuenta = desc_cuenta.cuenta.tipo or 'Sin clasificar'
            debe = float(desc_cuenta.debe or 0)
            haber = float(desc_cuenta.haber or 0)
            diferencia = (debe - haber) / float(comp.tipocambio or 1)
            
            cuenta_info = {
                'codigo': desc_cuenta.cuenta.codigo,
                'nombre': desc_cuenta.cuenta.nombre,
                'debe': debe,
                'haber': haber,
                'diferencia': round(diferencia, 2),
                'comprobante': comp
            }
            
            comprobantes_por_seccion[tipo_cuenta][comp.id].append(cuenta_info)
    
    # Convertir a formato para template
    secciones_lista = []
    for tipo_cuenta, comprobantes_dict in sorted(comprobantes_por_seccion.items()):
        comprobantes_con_cuentas = []
        for comp_id, cuentas_lista in comprobantes_dict.items():
            comp = next((c for c in comprobantes if c.id == comp_id), None)
            if comp:
                total_debe_seccion = sum(c['debe'] for c in cuentas_lista)
                total_haber_seccion = sum(c['haber'] for c in cuentas_lista)
                total_diff_seccion = sum(c['diferencia'] for c in cuentas_lista)
                
                comprobantes_con_cuentas.append({
                    'comprobante': comp,
                    'cuentas': cuentas_lista,
                    'total_debe': total_debe_seccion,
                    'total_haber': total_haber_seccion,
                    'total_diferencia': round(total_diff_seccion, 2)
                })
        
        secciones_lista.append({
            'tipo_cuenta': tipo_cuenta,
            'comprobantes': comprobantes_con_cuentas
        })
    
    return render(request, 'libros/detalle_libro.html', {
        'tipo': tipo,
        'tipo_nombre': tipo_nombre,
        'secciones': secciones_lista
    })
