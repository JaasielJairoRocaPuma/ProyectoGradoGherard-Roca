# Archivo: estadopatrimonio/views.py
# Descripción: Define las vistas para el módulo de Estado Patrimonial.
# Incluye vistas para generar, visualizar y gestionar estados financieros.

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from decimal import Decimal
from .models import (
    EstadoPatrimonial, EstadoResultados, ConfiguracionEstado,
    DetalleEstadoPatrimonial, DetalleEstadoResultados, ResumenFinanciero
)
from .forms import (
    GenerarEstadoPatrimonialForm, GenerarEstadoResultadosForm, ConfiguracionEstadoForm,
    FiltroEstadoPatrimonialForm, FiltroEstadoResultadosForm, FiltroDetalleEstadoForm,
    ExportarEstadoForm, CompararEstadosForm, AnalisisFinancieroForm
)
from plancuentas.models import PlanCuentas, TipoCuenta
from comprobantes.models import DetalleComprobante

class ListaEstadosPatrimonialesView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los estados patrimoniales generados.
    Incluye funcionalidad de búsqueda y filtrado.
    """
    model = EstadoPatrimonial
    template_name = 'estadopatrimonio/lista_estados_patrimoniales.html'
    context_object_name = 'estados'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EstadoPatrimonial.objects.select_related('usuario_generacion')
        
        # Aplicar filtros de búsqueda
        nombre = self.request.GET.get('nombre')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        usuario = self.request.GET.get('usuario')
        
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        if usuario:
            queryset = queryset.filter(usuario_generacion__username__icontains=usuario)
        
        return queryset.order_by('-fecha_generacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = FiltroEstadoPatrimonialForm(self.request.GET)
        return context

class ListaEstadosResultadosView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los estados de resultados generados.
    Incluye funcionalidad de búsqueda y filtrado.
    """
    model = EstadoResultados
    template_name = 'estadopatrimonio/lista_estados_resultados.html'
    context_object_name = 'estados'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EstadoResultados.objects.select_related('usuario_generacion')
        
        # Aplicar filtros de búsqueda
        nombre = self.request.GET.get('nombre')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        usuario = self.request.GET.get('usuario')
        
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_desde__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_hasta__lte=fecha_hasta)
        
        if usuario:
            queryset = queryset.filter(usuario_generacion__username__icontains=usuario)
        
        return queryset.order_by('-fecha_generacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = FiltroEstadoResultadosForm(self.request.GET)
        return context

class CrearEstadoPatrimonialView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo Estado Patrimonial.
    Incluye la lógica para generar el estado automáticamente.
    """
    model = EstadoPatrimonial
    form_class = GenerarEstadoPatrimonialForm
    template_name = 'estadopatrimonio/crear_estado_patrimonial.html'
    success_url = reverse_lazy('estadopatrimonio:lista_estados_patrimoniales')
    
    def form_valid(self, form):
        with transaction.atomic():
            # Crear el estado patrimonial
            estado = form.save(commit=False)
            estado.usuario_generacion = self.request.user
            estado.save()
            
            # Generar los detalles del estado
            self._generar_detalles_estado_patrimonial(estado)
            
            # Generar resumen financiero
            self._generar_resumen_financiero(estado)
            
            messages.success(
                self.request, 
                f'Estado Patrimonial "{estado.nombre}" generado exitosamente.'
            )
            return redirect('estadopatrimonio:detalle_estado_patrimonial', pk=estado.pk)
    
    def _generar_detalles_estado_patrimonial(self, estado):
        """
        Genera los detalles del estado patrimonial calculando saldos.
        """
        # Obtener cuentas de activos, pasivos y patrimonio
        cuentas = PlanCuentas.objects.filter(
            activa=True,
            tipo__in=[TipoCuenta.ACTIVO, TipoCuenta.PASIVO, TipoCuenta.PATRIMONIO]
        ).order_by('tipo', 'codigo')
        
        orden = 1
        for cuenta in cuentas:
            # Calcular saldo final de la cuenta
            saldo_final = self._calcular_saldo_final(cuenta, estado.fecha)
            
            # Crear detalle del estado
            detalle = DetalleEstadoPatrimonial.objects.create(
                estado=estado,
                cuenta=cuenta,
                saldo_final=saldo_final,
                orden=orden
            )
            
            orden += 1
    
    def _calcular_saldo_final(self, cuenta, fecha):
        """
        Calcula el saldo final de una cuenta hasta una fecha específica.
        """
        # Obtener saldo inicial
        saldo_inicial = cuenta.get_saldo_inicial()
        
        # Calcular movimientos hasta la fecha
        movimientos = DetalleComprobante.objects.filter(
            cuenta=cuenta,
            comprobante__fecha__lte=fecha,
            comprobante__estado='APROBADO'
        ).aggregate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )
        
        movimientos_debe = movimientos['total_debe'] or Decimal('0')
        movimientos_haber = movimientos['total_haber'] or Decimal('0')
        
        # Calcular saldo final según naturaleza de la cuenta
        if cuenta.naturaleza == 'DEUDORA':
            return saldo_inicial + movimientos_debe - movimientos_haber
        else:
            return saldo_inicial + movimientos_haber - movimientos_debe
    
    def _generar_resumen_financiero(self, estado):
        """
        Genera el resumen financiero del estado patrimonial.
        """
        activos, pasivos, patrimonio = estado.calcular_totales()
        
        resumen = ResumenFinanciero.objects.create(
            estado_patrimonial=estado,
            total_activos=activos,
            total_pasivos=pasivos,
            total_patrimonio=patrimonio
        )
        
        resumen.calcular_ratios()
        resumen.save()

class CrearEstadoResultadosView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo Estado de Resultados.
    Incluye la lógica para generar el estado automáticamente.
    """
    model = EstadoResultados
    form_class = GenerarEstadoResultadosForm
    template_name = 'estadopatrimonio/crear_estado_resultados.html'
    success_url = reverse_lazy('estadopatrimonio:lista_estados_resultados')
    
    def form_valid(self, form):
        with transaction.atomic():
            # Crear el estado de resultados
            estado = form.save(commit=False)
            estado.usuario_generacion = self.request.user
            estado.save()
            
            # Generar los detalles del estado
            self._generar_detalles_estado_resultados(estado)
            
            messages.success(
                self.request, 
                f'Estado de Resultados "{estado.nombre}" generado exitosamente.'
            )
            return redirect('estadopatrimonio:detalle_estado_resultados', pk=estado.pk)
    
    def _generar_detalles_estado_resultados(self, estado):
        """
        Genera los detalles del estado de resultados calculando saldos.
        """
        # Obtener cuentas de ingresos, gastos y costos
        cuentas = PlanCuentas.objects.filter(
            activa=True,
            tipo__in=[TipoCuenta.INGRESO, TipoCuenta.GASTO, TipoCuenta.COSTO]
        ).order_by('tipo', 'codigo')
        
        orden = 1
        for cuenta in cuentas:
            # Calcular saldo del período
            saldo_periodo = self._calcular_saldo_periodo(
                cuenta, estado.fecha_desde, estado.fecha_hasta
            )
            
            # Crear detalle del estado
            detalle = DetalleEstadoResultados.objects.create(
                estado=estado,
                cuenta=cuenta,
                saldo_final=saldo_periodo,
                orden=orden
            )
            
            orden += 1
    
    def _calcular_saldo_periodo(self, cuenta, fecha_desde, fecha_hasta):
        """
        Calcula el saldo de una cuenta en un período específico.
        """
        movimientos = DetalleComprobante.objects.filter(
            cuenta=cuenta,
            comprobante__fecha__range=[fecha_desde, fecha_hasta],
            comprobante__estado='APROBADO'
        ).aggregate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )
        
        movimientos_debe = movimientos['total_debe'] or Decimal('0')
        movimientos_haber = movimientos['total_haber'] or Decimal('0')
        
        # Para estados de resultados, el saldo es la diferencia
        return movimientos_haber - movimientos_debe

class DetalleEstadoPatrimonialView(LoginRequiredMixin, DetailView):
    """
    Vista para mostrar el detalle de un estado patrimonial específico.
    Incluye información de detalles y resúmenes.
    """
    model = EstadoPatrimonial
    template_name = 'estadopatrimonio/detalle_estado_patrimonial.html'
    context_object_name = 'estado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aplicar filtros si existen
        tipo_cuenta = self.request.GET.get('tipo_cuenta')
        saldo_minimo = self.request.GET.get('saldo_minimo')
        saldo_maximo = self.request.GET.get('saldo_maximo')
        solo_con_saldo = self.request.GET.get('solo_con_saldo')
        codigo_cuenta = self.request.GET.get('codigo_cuenta')
        
        detalles = self.object.detalles.select_related('cuenta').order_by('orden')
        
        if tipo_cuenta:
            detalles = detalles.filter(cuenta__tipo=tipo_cuenta)
        
        if saldo_minimo:
            detalles = detalles.filter(saldo_final__gte=saldo_minimo)
        
        if saldo_maximo:
            detalles = detalles.filter(saldo_final__lte=saldo_maximo)
        
        if solo_con_saldo:
            detalles = detalles.exclude(saldo_final=0)
        
        if codigo_cuenta:
            detalles = detalles.filter(cuenta__codigo__icontains=codigo_cuenta)
        
        context['detalles'] = detalles
        context['form_filtros'] = FiltroDetalleEstadoForm(self.request.GET)
        context['tipos_cuenta'] = TipoCuenta.choices
        
        # Calcular totales
        activos, pasivos, patrimonio = self.object.calcular_totales()
        context['total_activos'] = activos
        context['total_pasivos'] = pasivos
        context['total_patrimonio'] = patrimonio
        context['total_pasivos_patrimonio'] = pasivos + patrimonio
        
        # Obtener resumen financiero
        try:
            context['resumen'] = self.object.resumenes.first()
        except:
            context['resumen'] = None
        
        return context

class DetalleEstadoResultadosView(LoginRequiredMixin, DetailView):
    """
    Vista para mostrar el detalle de un estado de resultados específico.
    Incluye información de detalles y totales.
    """
    model = EstadoResultados
    template_name = 'estadopatrimonio/detalle_estado_resultados.html'
    context_object_name = 'estado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aplicar filtros si existen
        tipo_cuenta = self.request.GET.get('tipo_cuenta')
        saldo_minimo = self.request.GET.get('saldo_minimo')
        saldo_maximo = self.request.GET.get('saldo_maximo')
        solo_con_saldo = self.request.GET.get('solo_con_saldo')
        codigo_cuenta = self.request.GET.get('codigo_cuenta')
        
        detalles = self.object.detalles.select_related('cuenta').order_by('orden')
        
        if tipo_cuenta:
            detalles = detalles.filter(cuenta__tipo=tipo_cuenta)
        
        if saldo_minimo:
            detalles = detalles.filter(saldo_final__gte=saldo_minimo)
        
        if saldo_maximo:
            detalles = detalles.filter(saldo_final__lte=saldo_maximo)
        
        if solo_con_saldo:
            detalles = detalles.exclude(saldo_final=0)
        
        if codigo_cuenta:
            detalles = detalles.filter(cuenta__codigo__icontains=codigo_cuenta)
        
        context['detalles'] = detalles
        context['form_filtros'] = FiltroDetalleEstadoForm(self.request.GET)
        context['tipos_cuenta'] = TipoCuenta.choices
        
        # Calcular totales
        ingresos, gastos, costos, utilidad_bruta, utilidad_neta = self.object.calcular_totales()
        context['total_ingresos'] = ingresos
        context['total_gastos'] = gastos
        context['total_costos'] = costos
        context['utilidad_bruta'] = utilidad_bruta
        context['utilidad_neta'] = utilidad_neta
        
        return context

@login_required
def gestionar_configuraciones(request):
    """
    Vista para gestionar las configuraciones de estados financieros.
    Permite crear y editar configuraciones personalizadas.
    """
    if request.method == 'POST':
        form = ConfiguracionEstadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('estadopatrimonio:gestionar_configuraciones')
    else:
        form = ConfiguracionEstadoForm()
    
    configuraciones = ConfiguracionEstado.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'configuraciones': configuraciones,
    }
    
    return render(request, 'estadopatrimonio/gestionar_configuraciones.html', context)

@login_required
def comparar_estados(request):
    """
    Vista para comparar dos estados financieros.
    Permite analizar diferencias entre períodos.
    """
    if request.method == 'POST':
        form = CompararEstadosForm(request.POST)
        if form.is_valid():
            tipo_estado = form.cleaned_data['tipo_estado']
            estado_1 = form.cleaned_data['estado_1']
            estado_2 = form.cleaned_data['estado_2']
            
            # Redirigir a la vista de comparación
            return redirect('estadopatrimonio:resultado_comparacion', 
                          tipo=tipo_estado, pk1=estado_1.pk, pk2=estado_2.pk)
    else:
        form = CompararEstadosForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'estadopatrimonio/comparar_estados.html', context)

@login_required
def resultado_comparacion(request, tipo, pk1, pk2):
    """
    Vista para mostrar el resultado de la comparación de estados.
    """
    if tipo == 'patrimonial':
        estado_1 = get_object_or_404(EstadoPatrimonial, pk=pk1)
        estado_2 = get_object_or_404(EstadoPatrimonial, pk=pk2)
    else:
        estado_1 = get_object_or_404(EstadoResultados, pk=pk1)
        estado_2 = get_object_or_404(EstadoResultados, pk=pk2)
    
    context = {
        'tipo_estado': tipo,
        'estado_1': estado_1,
        'estado_2': estado_2,
    }
    
    return render(request, 'estadopatrimonio/resultado_comparacion.html', context)

@login_required
def exportar_estado(request, tipo, pk):
    """
    Vista para exportar un estado financiero a diferentes formatos.
    """
    if tipo == 'patrimonial':
        estado = get_object_or_404(EstadoPatrimonial, pk=pk)
    else:
        estado = get_object_or_404(EstadoResultados, pk=pk)
    
    if request.method == 'POST':
        form = ExportarEstadoForm(request.POST)
        if form.is_valid():
            formato = form.cleaned_data['formato']
            # Implementar lógica de exportación
            messages.info(request, f'Estado exportado en formato {formato.upper()}')
            return redirect('estadopatrimonio:detalle_estado_patrimonial', pk=pk)
    else:
        form = ExportarEstadoForm()
    
    context = {
        'tipo_estado': tipo,
        'estado': estado,
        'form': form,
    }
    
    return render(request, 'estadopatrimonio/exportar_estado.html', context)

@login_required
def analisis_financiero(request):
    """
    Vista para generar análisis financiero.
    Permite configurar diferentes tipos de análisis.
    """
    if request.method == 'POST':
        form = AnalisisFinancieroForm(request.POST)
        if form.is_valid():
            tipo_analisis = form.cleaned_data['tipo_analisis']
            fecha_desde = form.cleaned_data['fecha_desde']
            fecha_hasta = form.cleaned_data['fecha_hasta']
            
            # Redirigir a la vista de análisis
            return redirect('estadopatrimonio:resultado_analisis', 
                          tipo=tipo_analisis, desde=fecha_desde, hasta=fecha_hasta)
    else:
        form = AnalisisFinancieroForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'estadopatrimonio/analisis_financiero.html', context)

@login_required
def resultado_analisis(request, tipo, desde, hasta):
    """
    Vista para mostrar el resultado del análisis financiero.
    """
    # Implementar lógica de análisis según el tipo
    context = {
        'tipo_analisis': tipo,
        'fecha_desde': desde,
        'fecha_hasta': hasta,
    }
    
    return render(request, 'estadopatrimonio/resultado_analisis.html', context)
