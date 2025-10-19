# Archivo: balancesumasysaldos/forms.py
# Descripción: Define los formularios para el módulo de Balance de Sumas y Saldos.
# Incluye formularios para generar reportes y configurar balances.

from django import forms
from django.core.exceptions import ValidationError
from .models import BalanceSumasSaldos, ConfiguracionBalance
from plancuentas.models import TipoCuenta

class GenerarBalanceForm(forms.ModelForm):
    """
    Formulario para generar un nuevo Balance de Sumas y Saldos.
    Permite configurar el período y opciones del reporte.
    """
    class Meta:
        model = BalanceSumasSaldos
        fields = [
            'nombre', 'fecha_desde', 'fecha_hasta', 
            'incluir_saldos_cero', 'solo_cuentas_movimiento', 'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del reporte'
            }),
            'fecha_desde': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_hasta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'incluir_saldos_cero': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'solo_cuentas_movimiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del reporte'
            }),
        }
        labels = {
            'nombre': 'Nombre del Reporte',
            'fecha_desde': 'Fecha Desde',
            'fecha_hasta': 'Fecha Hasta',
            'incluir_saldos_cero': 'Incluir Saldos Cero',
            'solo_cuentas_movimiento': 'Solo Cuentas con Movimiento',
            'observaciones': 'Observaciones',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise ValidationError("La fecha desde no puede ser mayor a la fecha hasta.")
        
        return cleaned_data

class ConfiguracionBalanceForm(forms.ModelForm):
    """
    Formulario para configurar la generación de balances.
    Permite personalizar la forma en que se generan los reportes.
    """
    class Meta:
        model = ConfiguracionBalance
        fields = [
            'nombre', 'incluir_saldos_cero', 'solo_cuentas_movimiento',
            'agrupar_por_tipo', 'mostrar_saldos_anteriores', 'mostrar_movimientos',
            'formato_numero', 'activa'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la configuración'
            }),
            'incluir_saldos_cero': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'solo_cuentas_movimiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agrupar_por_tipo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_saldos_anteriores': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_movimientos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'formato_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 0,000.00'
            }),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de Configuración',
            'incluir_saldos_cero': 'Incluir Saldos Cero',
            'solo_cuentas_movimiento': 'Solo Cuentas con Movimiento',
            'agrupar_por_tipo': 'Agrupar por Tipo de Cuenta',
            'mostrar_saldos_anteriores': 'Mostrar Saldos Anteriores',
            'mostrar_movimientos': 'Mostrar Movimientos',
            'formato_numero': 'Formato de Números',
            'activa': 'Configuración Activa',
        }

class FiltroBalanceForm(forms.Form):
    """
    Formulario para filtrar balances existentes.
    Permite buscar por diferentes criterios.
    """
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre'
        }),
        label="Nombre"
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Fecha Desde"
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Fecha Hasta"
    )
    usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por usuario'
        }),
        label="Usuario"
    )

class FiltroDetalleBalanceForm(forms.Form):
    """
    Formulario para filtrar detalles de balance.
    Permite filtrar por tipo de cuenta y otros criterios.
    """
    tipo_cuenta = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(TipoCuenta.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Cuenta"
    )
    saldo_minimo = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label="Saldo Mínimo"
    )
    saldo_maximo = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label="Saldo Máximo"
    )
    solo_con_saldo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Solo Cuentas con Saldo"
    )
    codigo_cuenta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código'
        }),
        label="Código de Cuenta"
    )

class ExportarBalanceForm(forms.Form):
    """
    Formulario para exportar balances a diferentes formatos.
    Permite seleccionar formato y opciones de exportación.
    """
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Formato de Exportación"
    )
    incluir_resumen = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Incluir Resumen por Tipo"
    )
    incluir_observaciones = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Incluir Observaciones"
    )
    agrupar_por_tipo = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Agrupar por Tipo de Cuenta"
    )

class CompararBalancesForm(forms.Form):
    """
    Formulario para comparar dos balances.
    Permite seleccionar balances para comparación.
    """
    balance_1 = forms.ModelChoiceField(
        queryset=BalanceSumasSaldos.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Balance 1"
    )
    balance_2 = forms.ModelChoiceField(
        queryset=BalanceSumasSaldos.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Balance 2"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar balances disponibles
        self.fields['balance_1'].queryset = BalanceSumasSaldos.objects.all().order_by('-fecha_generacion')
        self.fields['balance_2'].queryset = BalanceSumasSaldos.objects.all().order_by('-fecha_generacion')
    
    def clean(self):
        cleaned_data = super().clean()
        balance_1 = cleaned_data.get('balance_1')
        balance_2 = cleaned_data.get('balance_2')
        
        if balance_1 and balance_2 and balance_1 == balance_2:
            raise ValidationError("Debe seleccionar balances diferentes para la comparación.")
        
        return cleaned_data
