# Archivo: balancesumasysaldos/views.py
# Descripción: Define las vistas para el módulo de Balance de Sumas y Saldos.
# Incluye vistas para generar, visualizar y gestionar reportes contables.

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
    BalanceSumasSaldos, DetalleBalance, ConfiguracionBalance, 
    ResumenBalance
)
from .forms import (
    GenerarBalanceForm, ConfiguracionBalanceForm, FiltroBalanceForm,
    FiltroDetalleBalanceForm, ExportarBalanceForm, CompararBalancesForm
)
from plancuentas.models import PlanCuentas, TipoCuenta
from comprobantes.models import DetalleComprobante

class ListaBalancesView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los balances generados.
    Incluye funcionalidad de búsqueda y filtrado.
    """
    model = BalanceSumasSaldos
    template_name = 'balancesumasysaldos/lista_balances.html'
    context_object_name = 'balances'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BalanceSumasSaldos.objects.select_related('usuario_generacion')
        
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
        context['form_busqueda'] = FiltroBalanceForm(self.request.GET)
        return context

class CrearBalanceView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo Balance de Sumas y Saldos.
    Incluye la lógica para generar el reporte automáticamente.
    """
    model = BalanceSumasSaldos
    form_class = GenerarBalanceForm
    template_name = 'balancesumasysaldos/crear_balance.html'
    success_url = reverse_lazy('balancesumasysaldos:lista_balances')
    
    def form_valid(self, form):
        with transaction.atomic():
            # Crear el balance
            balance = form.save(commit=False)
            balance.usuario_generacion = self.request.user
            balance.save()
            
            # Generar los detalles del balance
            self._generar_detalles_balance(balance)
            
            # Generar resúmenes por tipo de cuenta
            self._generar_resumenes_balance(balance)
            
            messages.success(
                self.request, 
                f'Balance "{balance.nombre}" generado exitosamente.'
            )
            return redirect('balancesumasysaldos:detalle_balance', pk=balance.pk)
    
    def _generar_detalles_balance(self, balance):
        """
        Genera los detalles del balance calculando saldos y movimientos.
        """
        # Obtener todas las cuentas activas
        cuentas = PlanCuentas.objects.filter(activa=True)
        
        if balance.solo_cuentas_movimiento:
            # Filtrar solo cuentas que tuvieron movimientos en el período
            cuentas_con_movimiento = DetalleComprobante.objects.filter(
                comprobante__fecha__range=[balance.fecha_desde, balance.fecha_hasta],
                comprobante__estado='APROBADO'
            ).values_list('cuenta_id', flat=True).distinct()
            
            cuentas = cuentas.filter(id__in=cuentas_con_movimiento)
        
        orden = 1
        for cuenta in cuentas:
            # Calcular saldo anterior (hasta fecha_desde)
            saldo_anterior = self._calcular_saldo_anterior(cuenta, balance.fecha_desde)
            
            # Calcular movimientos del período
            movimientos_debe, movimientos_haber = self._calcular_movimientos_periodo(
                cuenta, balance.fecha_desde, balance.fecha_hasta
            )
            
            # Calcular saldo final
            saldo_final = self._calcular_saldo_final(
                cuenta, saldo_anterior, movimientos_debe, movimientos_haber
            )
            
            # Determinar si incluir la cuenta
            if not balance.incluir_saldos_cero and saldo_final == 0:
                continue
            
            # Crear detalle del balance
            detalle = DetalleBalance.objects.create(
                balance=balance,
                cuenta=cuenta,
                saldo_anterior=saldo_anterior,
                movimientos_debe=movimientos_debe,
                movimientos_haber=movimientos_haber,
                orden=orden
            )
            
            # Calcular y guardar saldo final
            detalle.calcular_saldo_final()
            detalle.save()
            
            orden += 1
    
    def _calcular_saldo_anterior(self, cuenta, fecha_desde):
        """
        Calcula el saldo anterior de una cuenta hasta una fecha específica.
        """
        # Obtener saldo inicial
        saldo_inicial = cuenta.get_saldo_inicial()
        
        # Calcular movimientos hasta fecha_desde
        movimientos = DetalleComprobante.objects.filter(
            cuenta=cuenta,
            comprobante__fecha__lt=fecha_desde,
            comprobante__estado='APROBADO'
        ).aggregate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )
        
        movimientos_debe = movimientos['total_debe'] or Decimal('0')
        movimientos_haber = movimientos['total_haber'] or Decimal('0')
        
        # Calcular saldo anterior según naturaleza de la cuenta
        if cuenta.naturaleza == 'DEUDORA':
            return saldo_inicial + movimientos_debe - movimientos_haber
        else:
            return saldo_inicial + movimientos_haber - movimientos_debe
    
    def _calcular_movimientos_periodo(self, cuenta, fecha_desde, fecha_hasta):
        """
        Calcula los movimientos de una cuenta en un período específico.
        """
        movimientos = DetalleComprobante.objects.filter(
            cuenta=cuenta,
            comprobante__fecha__range=[fecha_desde, fecha_hasta],
            comprobante__estado='APROBADO'
        ).aggregate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )
        
        return movimientos['total_debe'] or Decimal('0'), movimientos['total_haber'] or Decimal('0')
    
    def _calcular_saldo_final(self, cuenta, saldo_anterior, movimientos_debe, movimientos_haber):
        """
        Calcula el saldo final de una cuenta.
        """
        if cuenta.naturaleza == 'DEUDORA':
            return saldo_anterior + movimientos_debe - movimientos_haber
        else:
            return saldo_anterior + movimientos_haber - movimientos_debe
    
    def _generar_resumenes_balance(self, balance):
        """
        Genera resúmenes del balance por tipo de cuenta.
        """
        detalles = balance.detalles.all()
        
        for tipo_cuenta, _ in TipoCuenta.choices:
            detalles_tipo = detalles.filter(cuenta__tipo=tipo_cuenta)
            
            if detalles_tipo.exists():
                total_debe = sum(detalle.saldo_debe for detalle in detalles_tipo)
                total_haber = sum(detalle.saldo_haber for detalle in detalles_tipo)
                cantidad_cuentas = detalles_tipo.count()
                
                resumen = ResumenBalance.objects.create(
                    balance=balance,
                    tipo_cuenta=tipo_cuenta,
                    total_debe=total_debe,
                    total_haber=total_haber,
                    cantidad_cuentas=cantidad_cuentas
                )
                resumen.calcular_saldo_neto()
                resumen.save()

class DetalleBalanceView(LoginRequiredMixin, DetailView):
    """
    Vista para mostrar el detalle de un balance específico.
    Incluye información de detalles y resúmenes.
    """
    model = BalanceSumasSaldos
    template_name = 'balancesumasysaldos/detalle_balance.html'
    context_object_name = 'balance'
    
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
        context['resumenes'] = self.object.resumenes.all().order_by('tipo_cuenta')
        context['form_filtros'] = FiltroDetalleBalanceForm(self.request.GET)
        context['tipos_cuenta'] = TipoCuenta.choices
        
        # Calcular totales
        total_debe, total_haber = self.object.calcular_totales()
        context['total_debe'] = total_debe
        context['total_haber'] = total_haber
        context['diferencia'] = total_debe - total_haber
        
        return context

@login_required
def gestionar_configuraciones(request):
    """
    Vista para gestionar las configuraciones de balance.
    Permite crear y editar configuraciones personalizadas.
    """
    if request.method == 'POST':
        form = ConfiguracionBalanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('balancesumasysaldos:gestionar_configuraciones')
    else:
        form = ConfiguracionBalanceForm()
    
    configuraciones = ConfiguracionBalance.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'configuraciones': configuraciones,
    }
    
    return render(request, 'balancesumasysaldos/gestionar_configuraciones.html', context)

@login_required
def comparar_balances(request):
    """
    Vista para comparar dos balances.
    Permite analizar diferencias entre períodos.
    """
    if request.method == 'POST':
        form = CompararBalancesForm(request.POST)
        if form.is_valid():
            balance_1 = form.cleaned_data['balance_1']
            balance_2 = form.cleaned_data['balance_2']
            
            # Redirigir a la vista de comparación
            return redirect('balancesumasysaldos:resultado_comparacion', 
                          pk1=balance_1.pk, pk2=balance_2.pk)
    else:
        form = CompararBalancesForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'balancesumasysaldos/comparar_balances.html', context)

@login_required
def resultado_comparacion(request, pk1, pk2):
    """
    Vista para mostrar el resultado de la comparación de balances.
    """
    balance_1 = get_object_or_404(BalanceSumasSaldos, pk=pk1)
    balance_2 = get_object_or_404(BalanceSumasSaldos, pk=pk2)
    
    # Implementar lógica de comparación
    # Por ahora, solo mostrar los balances lado a lado
    context = {
        'balance_1': balance_1,
        'balance_2': balance_2,
    }
    
    return render(request, 'balancesumasysaldos/resultado_comparacion.html', context)

@login_required
def exportar_balance(request, pk):
    """
    Vista para exportar un balance a diferentes formatos.
    """
    balance = get_object_or_404(BalanceSumasSaldos, pk=pk)
    
    if request.method == 'POST':
        form = ExportarBalanceForm(request.POST)
        if form.is_valid():
            formato = form.cleaned_data['formato']
            # Implementar lógica de exportación
            messages.info(request, f'Balance exportado en formato {formato.upper()}')
            return redirect('balancesumasysaldos:detalle_balance', pk=pk)
    else:
        form = ExportarBalanceForm()
    
    context = {
        'balance': balance,
        'form': form,
    }
    
    return render(request, 'balancesumasysaldos/exportar_balance.html', context)
