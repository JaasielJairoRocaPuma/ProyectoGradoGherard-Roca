# Archivo: comprobantes/views.py
# Descripción: Define las vistas para el módulo de comprobantes contables.
# Incluye vistas para crear, editar, aprobar y gestionar comprobantes.

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from .models import Comprobante, DetalleComprobante, SecuenciaComprobante, TipoComprobante, EstadoComprobante
from .forms import (
    ComprobanteForm, DetalleComprobanteForm, DetalleComprobanteFormSet,
    BuscarComprobanteForm, SecuenciaComprobanteForm, AprobarComprobanteForm
)

class ListaComprobantesView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los comprobantes.
    Incluye funcionalidad de búsqueda y filtrado.
    """
    model = Comprobante
    template_name = 'comprobantes/lista_comprobantes.html'
    context_object_name = 'comprobantes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Comprobante.objects.select_related('usuario_creacion', 'usuario_aprobacion')
        
        # Aplicar filtros de búsqueda
        numero = self.request.GET.get('numero')
        tipo = self.request.GET.get('tipo')
        estado = self.request.GET.get('estado')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        concepto = self.request.GET.get('concepto')
        
        if numero:
            queryset = queryset.filter(numero__icontains=numero)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        if concepto:
            queryset = queryset.filter(concepto__icontains=concepto)
        
        return queryset.order_by('-fecha', '-numero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = BuscarComprobanteForm(self.request.GET)
        context['tipos_comprobante'] = TipoComprobante.choices
        context['estados'] = EstadoComprobante.choices
        return context

class CrearComprobanteView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo comprobante.
    Incluye manejo de detalles con formset.
    """
    model = Comprobante
    form_class = ComprobanteForm
    template_name = 'comprobantes/crear_comprobante.html'
    success_url = reverse_lazy('comprobantes:lista_comprobantes')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles_formset'] = DetalleComprobanteFormSet(self.request.POST)
        else:
            context['detalles_formset'] = DetalleComprobanteFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detalles_formset = context['detalles_formset']
        
        if detalles_formset.is_valid():
            with transaction.atomic():
                # Generar número de comprobante
                comprobante = form.save(commit=False)
                comprobante.usuario_creacion = self.request.user
                comprobante.numero = self._generar_numero_comprobante(comprobante.tipo)
                comprobante.save()
                
                # Guardar detalles
                detalles_formset.instance = comprobante
                detalles_formset.save()
                
                # Calcular totales
                comprobante.calcular_totales()
                
                messages.success(
                    self.request, 
                    f'Comprobante "{comprobante.numero}" creado exitosamente.'
                )
                return redirect(self.success_url)
        else:
            return self.form_invalid(form)
    
    def _generar_numero_comprobante(self, tipo):
        """
        Genera el siguiente número de comprobante para el tipo especificado.
        """
        secuencia, created = SecuenciaComprobante.objects.get_or_create(
            tipo=tipo,
            defaults={
                'prefijo': self._get_prefijo_default(tipo),
                'formato': '000000'
            }
        )
        
        numero = secuencia.obtener_siguiente_numero()
        return secuencia.formatear_numero(numero)
    
    def _get_prefijo_default(self, tipo):
        """
        Obtiene el prefijo por defecto según el tipo de comprobante.
        """
        prefijos = {
            TipoComprobante.INGRESO: 'CI',
            TipoComprobante.EGRESO: 'CE',
            TipoComprobante.DIARIO: 'AD',
            TipoComprobante.TRASPASO: 'AT',
            TipoComprobante.AJUSTE: 'AA',
        }
        return prefijos.get(tipo, '')

class EditarComprobanteView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar un comprobante existente.
    Solo permite edición si está en estado borrador.
    """
    model = Comprobante
    form_class = ComprobanteForm
    template_name = 'comprobantes/editar_comprobante.html'
    success_url = reverse_lazy('comprobantes:lista_comprobantes')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles_formset'] = DetalleComprobanteFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['detalles_formset'] = DetalleComprobanteFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detalles_formset = context['detalles_formset']
        
        if detalles_formset.is_valid():
            with transaction.atomic():
                comprobante = form.save()
                detalles_formset.save()
                comprobante.calcular_totales()
                
                messages.success(
                    self.request, 
                    f'Comprobante "{comprobante.numero}" actualizado exitosamente.'
                )
                return redirect(self.success_url)
        else:
            return self.form_invalid(form)
    
    def get_queryset(self):
        # Solo permitir edición de comprobantes en borrador
        return Comprobante.objects.filter(estado=EstadoComprobante.BORRADOR)

class DetalleComprobanteView(LoginRequiredMixin, DetailView):
    """
    Vista para mostrar el detalle de un comprobante.
    Incluye información de detalles y totales.
    """
    model = Comprobante
    template_name = 'comprobantes/detalle_comprobante.html'
    context_object_name = 'comprobante'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] = self.object.detalles.select_related('cuenta').order_by('orden')
        context['puede_editar'] = self.object.estado == EstadoComprobante.BORRADOR
        context['puede_aprobar'] = self.object.estado == EstadoComprobante.BORRADOR
        context['puede_anular'] = self.object.estado in [
            EstadoComprobante.BORRADOR, 
            EstadoComprobante.PENDIENTE
        ]
        return context

@login_required
def aprobar_comprobante(request, pk):
    """
    Vista para aprobar un comprobante.
    Cambia el estado de borrador a aprobado.
    """
    comprobante = get_object_or_404(Comprobante, pk=pk)
    
    if comprobante.estado != EstadoComprobante.BORRADOR:
        messages.error(request, 'Solo se pueden aprobar comprobantes en estado borrador.')
        return redirect('comprobantes:detalle_comprobante', pk=pk)
    
    if not comprobante.es_balanceado():
        messages.error(request, 'El comprobante no está balanceado. No se puede aprobar.')
        return redirect('comprobantes:detalle_comprobante', pk=pk)
    
    if request.method == 'POST':
        form = AprobarComprobanteForm(request.POST, comprobante=comprobante)
        if form.is_valid():
            comprobante.aprobar(request.user)
            messages.success(request, f'Comprobante "{comprobante.numero}" aprobado exitosamente.')
            return redirect('comprobantes:detalle_comprobante', pk=pk)
    else:
        form = AprobarComprobanteForm(comprobante=comprobante)
    
    context = {
        'comprobante': comprobante,
        'form': form,
    }
    
    return render(request, 'comprobantes/aprobar_comprobante.html', context)

@login_required
def anular_comprobante(request, pk):
    """
    Vista para anular un comprobante.
    Cambia el estado a anulado.
    """
    comprobante = get_object_or_404(Comprobante, pk=pk)
    
    if comprobante.estado not in [EstadoComprobante.BORRADOR, EstadoComprobante.PENDIENTE]:
        messages.error(request, 'No se puede anular este comprobante.')
        return redirect('comprobantes:detalle_comprobante', pk=pk)
    
    if request.method == 'POST':
        comprobante.anular(request.user)
        messages.success(request, f'Comprobante "{comprobante.numero}" anulado exitosamente.')
        return redirect('comprobantes:detalle_comprobante', pk=pk)
    
    context = {
        'comprobante': comprobante,
    }
    
    return render(request, 'comprobantes/anular_comprobante.html', context)

@login_required
def gestionar_secuencias(request):
    """
    Vista para gestionar las secuencias de numeración.
    Permite configurar prefijos y formatos por tipo.
    """
    if request.method == 'POST':
        form = SecuenciaComprobanteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Secuencia configurada exitosamente.')
            return redirect('comprobantes:gestionar_secuencias')
    else:
        form = SecuenciaComprobanteForm()
    
    secuencias = SecuenciaComprobante.objects.all().order_by('tipo')
    
    context = {
        'form': form,
        'secuencias': secuencias,
    }
    
    return render(request, 'comprobantes/gestionar_secuencias.html', context)

@login_required
def buscar_cuenta_ajax(request):
    """
    Vista AJAX para buscar cuentas por código o nombre.
    Utilizada para autocompletar en formularios de detalles.
    """
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'cuentas': []})
    
    from plancuentas.models import PlanCuentas
    cuentas = PlanCuentas.objects.filter(
        Q(codigo__icontains=query) | Q(nombre__icontains=query),
        activa=True,
        permite_movimiento=True
    ).order_by('codigo')[:10]
    
    resultados = []
    for cuenta in cuentas:
        resultados.append({
            'id': cuenta.id,
            'codigo': cuenta.codigo,
            'nombre': cuenta.nombre,
            'tipo': cuenta.get_tipo_display(),
            'naturaleza': cuenta.get_naturaleza_display(),
        })
    
    return JsonResponse({'cuentas': resultados})

@login_required
def reporte_comprobantes(request):
    """
    Vista para generar reportes de comprobantes.
    Incluye filtros por fecha y tipo.
    """
    # Implementar lógica de reportes
    pass
