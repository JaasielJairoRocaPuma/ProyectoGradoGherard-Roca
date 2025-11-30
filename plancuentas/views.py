# Archivo: plancuentas/views.py
# Descripción: Define las vistas para el módulo de Plan de Cuentas.
# Incluye vistas para listar, crear, editar y gestionar cuentas contables.

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Grupo, SubGrupo, CuentaMatriz, CuentaMayor, CuentaAuxiliar
from .forms import CreateNewCuentaAuxiliar, EditCuentaAuxiliar

def ListaPlanCuentasView(request):
    grupos = Grupo.objects.all()
    subgrupos = SubGrupo.objects.all()
    cuentas_matriz = CuentaMatriz.objects.all()
    cuentas_mayor = CuentaMayor.objects.all()
    cuentas_auxiliar = CuentaAuxiliar.objects.all()

    if request.method == "GET":
        return render(request, 'plancuentas/lista_cuentas.html', {
            'grupos': grupos,
            'subgrupos': subgrupos,
            'cuentas_matriz': cuentas_matriz,
            'cuentas_mayor': cuentas_mayor,
            'cuentas_auxiliar': cuentas_auxiliar,
            'form': CreateNewCuentaAuxiliar(),
            'formE': EditCuentaAuxiliar()
            })
    else:
        if request.POST['type'] == 'crear':
            CuentaAuxiliar.objects.create(
                cod=request.POST['cod'],
                nombre=request.POST['nombre'],
                cuentamayor=get_object_or_404(CuentaMayor, id=request.POST['cuentamayor']),
                tipo=request.POST['tipo'],
            )
        elif request.POST['type']=='borrar':
            ca=CuentaAuxiliar.objects.filter(id=request.POST['id']).first()
            ca.delete()
        else:
            ca=CuentaAuxiliar.objects.filter(id=request.POST['id']).first()
            ca.nombre=request.POST['nombre']
            ca.save()
        return redirect(request.path)

    
    

# class CrearCuentaView(LoginRequiredMixin, CreateView):
#     """
#     Vista para crear una nueva cuenta en el Plan de Cuentas.
#     Incluye validaciones específicas para códigos y jerarquías.
#     """
#     model = PlanCuentas
#     form_class = PlanCuentasForm
#     template_name = 'plancuentas/crear_cuenta.html'
#     success_url = reverse_lazy('plancuentas:lista_cuentas')
    
#     def form_valid(self, form):
#         messages.success(
#             self.request, 
#             f'Cuenta "{form.instance.codigo} - {form.instance.nombre}" creada exitosamente.'
#         )
#         return super().form_valid(form)
    
#     def form_invalid(self, form):
#         messages.error(
#             self.request, 
#             'Por favor, corrija los errores en el formulario.'
#         )
#         return super().form_invalid(form)

# class EditarCuentaView(LoginRequiredMixin, UpdateView):
#     """
#     Vista para editar una cuenta existente en el Plan de Cuentas.
#     Mantiene la integridad de la jerarquía de cuentas.
#     """
#     model = PlanCuentas
#     form_class = PlanCuentasForm
#     template_name = 'plancuentas/editar_cuenta.html'
#     success_url = reverse_lazy('plancuentas:lista_cuentas')
    
#     def form_valid(self, form):
#         messages.success(
#             self.request, 
#             f'Cuenta "{form.instance.codigo} - {form.instance.nombre}" actualizada exitosamente.'
#         )
#         return super().form_valid(form)
    
#     def form_invalid(self, form):
#         messages.error(
#             self.request, 
#             'Por favor, corrija los errores en el formulario.'
#         )
#         return super().form_invalid(form)

# class EliminarCuentaView(LoginRequiredMixin, DeleteView):
#     """
#     Vista para eliminar una cuenta del Plan de Cuentas.
#     Incluye validaciones para evitar eliminación de cuentas con movimientos.
#     """
#     model = PlanCuentas
#     template_name = 'plancuentas/eliminar_cuenta.html'
#     success_url = reverse_lazy('plancuentas:lista_cuentas')
    
#     def delete(self, request, *args, **kwargs):
#         cuenta = self.get_object()
        
#         # Verificar si la cuenta tiene subcuentas
#         if cuenta.cuentas_hijas.exists():
#             messages.error(
#                 request, 
#                 f'No se puede eliminar la cuenta "{cuenta.codigo}" porque tiene subcuentas asociadas.'
#             )
#             return redirect('plancuentas:lista_cuentas')
        
#         # Verificar si la cuenta tiene movimientos (se implementará con comprobantes)
#         # if cuenta.tiene_movimientos():
#         #     messages.error(
#         #         request, 
#         #         f'No se puede eliminar la cuenta "{cuenta.codigo}" porque tiene movimientos registrados.'
#         #     )
#         #     return redirect('plancuentas:lista_cuentas')
        
#         messages.success(
#             request, 
#             f'Cuenta "{cuenta.codigo} - {cuenta.nombre}" eliminada exitosamente.'
#         )
#         return super().delete(request, *args, **kwargs)

# @login_required
# def detalle_cuenta(request, pk):
#     """
#     Vista para mostrar el detalle de una cuenta específica.
#     Incluye información de jerarquía y saldos.
#     """
#     cuenta = get_object_or_404(PlanCuentas, pk=pk)
    
#     # Obtener cuentas hijas
#     cuentas_hijas = cuenta.cuentas_hijas.all().order_by('codigo')
    
#     # Obtener saldo inicial
#     saldo_inicial = cuenta.get_saldo_inicial()
    
#     context = {
#         'cuenta': cuenta,
#         'cuentas_hijas': cuentas_hijas,
#         'saldo_inicial': saldo_inicial,
#     }
    
#     return render(request, 'plancuentas/detalle_cuenta.html', context)

# @login_required
# def gestionar_saldos_iniciales(request):
#     """
#     Vista para gestionar los saldos iniciales de las cuentas.
#     Permite establecer el estado inicial del Plan de Cuentas.
#     """
#     if request.method == 'POST':
#         form = SaldoInicialForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Saldo inicial registrado exitosamente.')
#             return redirect('plancuentas:gestionar_saldos')
#     else:
#         form = SaldoInicialForm()
    
#     # Obtener saldos iniciales existentes
#     saldos = SaldoInicial.objects.select_related('cuenta').order_by('cuenta__codigo')
    
#     context = {
#         'form': form,
#         'saldos': saldos,
#     }
    
#     return render(request, 'plancuentas/gestionar_saldos.html', context)

# @login_required
# def arbol_cuentas(request):
#     """
#     Vista para mostrar el Plan de Cuentas en formato de árbol.
#     Facilita la visualización de la jerarquía de cuentas.
#     """
#     # Obtener cuentas de nivel 1 (raíz)
#     cuentas_raiz = PlanCuentas.objects.filter(nivel=1, activa=True).order_by('codigo')
    
#     context = {
#         'cuentas_raiz': cuentas_raiz,
#     }
    
#     return render(request, 'plancuentas/arbol_cuentas.html', context)

# @login_required
# def buscar_cuenta_ajax(request):
#     """
#     Vista AJAX para buscar cuentas por código o nombre.
#     Utilizada para autocompletar en formularios.
#     """
#     query = request.GET.get('q', '')
    
#     if len(query) < 2:
#         return JsonResponse({'cuentas': []})
    
#     cuentas = PlanCuentas.objects.filter(
#         Q(codigo__icontains=query) | Q(nombre__icontains=query),
#         activa=True
#     ).order_by('codigo')[:10]
    
#     resultados = []
#     for cuenta in cuentas:
#         resultados.append({
#             'id': cuenta.id,
#             'codigo': cuenta.codigo,
#             'nombre': cuenta.nombre,
#             'tipo': cuenta.get_tipo_display(),
#             'naturaleza': cuenta.get_naturaleza_display(),
#         })
    
#     return JsonResponse({'cuentas': resultados})

# @login_required
# def exportar_plan_cuentas(request):
#     """
#     Vista para exportar el Plan de Cuentas a diferentes formatos.
#     Soporta exportación a CSV y Excel.
#     """
#     formato = request.GET.get('formato', 'csv')
    
#     if formato == 'csv':
#         # Implementar exportación CSV
#         pass
#     elif formato == 'excel':
#         # Implementar exportación Excel
#         pass
    
#     messages.info(request, f'Plan de Cuentas exportado en formato {formato.upper()}')
#     return redirect('plancuentas:lista_cuentas')
