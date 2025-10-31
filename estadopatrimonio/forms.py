# Archivo: estadopatrimonio/forms.py
# Descripción: Define los formularios para el módulo de Estado Patrimonial.
# Incluye formularios para generar estados financieros y configuraciones.

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    EstadoPatrimonial, EstadoResultados, ConfiguracionEstado, 
    DetalleEstadoPatrimonial, DetalleEstadoResultados
)
from plancuentas.models import TipoCuenta

class GenerarEstadoPatrimonialForm(forms.ModelForm):
    """
    Formulario para generar un nuevo Estado Patrimonial.
    Permite configurar la fecha de corte y opciones del estado.
    """
    class Meta:
        model = EstadoPatrimonial
        fields = ['nombre', 'fecha', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del estado patrimonial'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del estado'
            }),
        }
        labels = {
            'nombre': 'Nombre del Estado',
            'fecha': 'Fecha de Corte',
            'observaciones': 'Observaciones',
        }

class GenerarEstadoResultadosForm(forms.ModelForm):
    """
    Formulario para generar un nuevo Estado de Resultados.
    Permite configurar el período y opciones del estado.
    """
    class Meta:
        model = EstadoResultados
        fields = ['nombre', 'fecha_desde', 'fecha_hasta', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del estado de resultados'
            }),
            'fecha_desde': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_hasta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del estado'
            }),
        }
        labels = {
            'nombre': 'Nombre del Estado',
            'fecha_desde': 'Fecha Desde',
            'fecha_hasta': 'Fecha Hasta',
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

class ConfiguracionEstadoForm(forms.ModelForm):
    """
    Formulario para configurar la generación de estados financieros.
    Permite personalizar la forma en que se generan los estados.
    """
    class Meta:
        model = ConfiguracionEstado
        fields = [
            'nombre', 'incluir_saldos_cero', 'agrupar_por_tipo',
            'mostrar_cuentas_principales', 'formato_numero', 'activa'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la configuración'
            }),
            'incluir_saldos_cero': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agrupar_por_tipo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_cuentas_principales': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'formato_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 0,000.00'
            }),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de Configuración',
            'incluir_saldos_cero': 'Incluir Saldos Cero',
            'agrupar_por_tipo': 'Agrupar por Tipo de Cuenta',
            'mostrar_cuentas_principales': 'Mostrar Solo Cuentas Principales',
            'formato_numero': 'Formato de Números',
            'activa': 'Configuración Activa',
        }

class FiltroEstadoPatrimonialForm(forms.Form):
    """
    Formulario para filtrar estados patrimoniales.
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

class FiltroEstadoResultadosForm(forms.Form):
    """
    Formulario para filtrar estados de resultados.
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

class FiltroDetalleEstadoForm(forms.Form):
    """
    Formulario para filtrar detalles de estados financieros.
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

class ExportarEstadoForm(forms.Form):
    """
    Formulario para exportar estados financieros a diferentes formatos.
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
        label="Incluir Resumen Financiero"
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

class CompararEstadosForm(forms.Form):
    """
    Formulario para comparar dos estados financieros.
    Permite seleccionar estados para comparación.
    """
    TIPO_ESTADO_CHOICES = [
        ('patrimonial', 'Estado Patrimonial'),
        ('resultados', 'Estado de Resultados'),
    ]
    
    tipo_estado = forms.ChoiceField(
        choices=TIPO_ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Estado"
    )
    estado_1 = forms.ModelChoiceField(
        queryset=EstadoPatrimonial.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado 1"
    )
    estado_2 = forms.ModelChoiceField(
        queryset=EstadoPatrimonial.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado 2"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar estados disponibles según el tipo
        self.fields['estado_1'].queryset = EstadoPatrimonial.objects.all().order_by('-fecha_generacion')
        self.fields['estado_2'].queryset = EstadoPatrimonial.objects.all().order_by('-fecha_generacion')
    
    def clean(self):
        cleaned_data = super().clean()
        estado_1 = cleaned_data.get('estado_1')
        estado_2 = cleaned_data.get('estado_2')
        
        if estado_1 and estado_2 and estado_1 == estado_2:
            raise ValidationError("Debe seleccionar estados diferentes para la comparación.")
        
        return cleaned_data

class AnalisisFinancieroForm(forms.Form):
    """
    Formulario para configurar análisis financiero.
    Permite seleccionar períodos y tipos de análisis.
    """
    TIPO_ANALISIS_CHOICES = [
        ('ratios', 'Análisis de Ratios'),
        ('tendencias', 'Análisis de Tendencias'),
        ('comparativo', 'Análisis Comparativo'),
        ('vertical', 'Análisis Vertical'),
        ('horizontal', 'Análisis Horizontal'),
    ]
    
    tipo_analisis = forms.ChoiceField(
        choices=TIPO_ANALISIS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Análisis"
    )
    fecha_desde = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Fecha Desde"
    )
    fecha_hasta = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Fecha Hasta"
    )
    incluir_graficos = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Incluir Gráficos"
    )
    incluir_recomendaciones = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Incluir Recomendaciones"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise ValidationError("La fecha desde no puede ser mayor a la fecha hasta.")
        
        return cleaned_data
