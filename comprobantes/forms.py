# Archivo: comprobantes/forms.py
# Descripción: Define los formularios para el módulo de comprobantes contables.
# Incluye formularios para crear, editar y gestionar comprobantes.

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Comprobante, DetalleComprobante, SecuenciaComprobante, TipoComprobante, EstadoComprobante
from plancuentas.models import PlanCuentas

class ComprobanteForm(forms.ModelForm):
    """
    Formulario para crear y editar comprobantes contables.
    Incluye validaciones específicas para el balance de cuentas.
    """
    class Meta:
        model = Comprobante
        fields = [
            'tipo', 'fecha', 'concepto', 'referencia', 'observaciones'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'concepto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del comprobante'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia externa'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales'
            }),
        }
        labels = {
            'tipo': 'Tipo de Comprobante',
            'fecha': 'Fecha',
            'concepto': 'Concepto',
            'referencia': 'Referencia',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si es un nuevo comprobante, generar número automáticamente
        if not self.instance.pk:
            self.fields['numero'] = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'readonly': True
                }),
                label="Número de Comprobante",
                required=False
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que el comprobante esté balanceado
        if hasattr(self, 'detalles_formset'):
            total_debe = sum(
                detalle.cleaned_data.get('debe', 0) 
                for detalle in self.detalles_formset.forms 
                if detalle.cleaned_data and not detalle.cleaned_data.get('DELETE', False)
            )
            total_haber = sum(
                detalle.cleaned_data.get('haber', 0) 
                for detalle in self.detalles_formset.forms 
                if detalle.cleaned_data and not detalle.cleaned_data.get('DELETE', False)
            )
            
            if total_debe != total_haber:
                raise ValidationError(
                    f"El comprobante no está balanceado. Debe: {total_debe}, Haber: {total_haber}"
                )
        
        return cleaned_data

class DetalleComprobanteForm(forms.ModelForm):
    """
    Formulario para los detalles de un comprobante.
    Representa cada línea de débito o crédito.
    """
    class Meta:
        model = DetalleComprobante
        fields = ['cuenta', 'concepto', 'debe', 'haber', 'orden']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'concepto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Concepto del movimiento'
            }),
            'debe': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'haber': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
        labels = {
            'cuenta': 'Cuenta Contable',
            'concepto': 'Concepto',
            'debe': 'Debe',
            'haber': 'Haber',
            'orden': 'Orden',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo cuentas que permiten movimiento
        self.fields['cuenta'].queryset = PlanCuentas.objects.filter(
            activa=True, 
            permite_movimiento=True
        ).order_by('codigo')
        self.fields['cuenta'].empty_label = "Seleccione una cuenta"
    
    def clean(self):
        cleaned_data = super().clean()
        debe = cleaned_data.get('debe', 0)
        haber = cleaned_data.get('haber', 0)
        
        # Verificar que no se tenga debe y haber al mismo tiempo
        if debe > 0 and haber > 0:
            raise ValidationError("No se puede tener debe y haber al mismo tiempo.")
        
        # Verificar que al menos uno sea mayor a 0
        if debe == 0 and haber == 0:
            raise ValidationError("Debe o haber debe ser mayor a 0.")
        
        return cleaned_data

# Formset para manejar múltiples detalles
DetalleComprobanteFormSet = inlineformset_factory(
    Comprobante,
    DetalleComprobante,
    form=DetalleComprobanteForm,
    extra=2,  # Mostrar 2 líneas vacías por defecto
    can_delete=True,
    min_num=1,  # Mínimo 1 detalle
    validate_min=True,
)

class BuscarComprobanteForm(forms.Form):
    """
    Formulario para buscar comprobantes.
    Permite filtrar por diferentes criterios.
    """
    numero = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número'
        }),
        label="Número"
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(TipoComprobante.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo"
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + list(EstadoComprobante.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado"
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
    concepto = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en concepto'
        }),
        label="Concepto"
    )

class SecuenciaComprobanteForm(forms.ModelForm):
    """
    Formulario para configurar las secuencias de numeración.
    Permite establecer prefijos y formatos por tipo de comprobante.
    """
    class Meta:
        model = SecuenciaComprobante
        fields = ['tipo', 'prefijo', 'siguiente_numero', 'formato', 'activo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'prefijo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CI, CE, AD'
            }),
            'siguiente_numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'formato': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 000000'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'tipo': 'Tipo de Comprobante',
            'prefijo': 'Prefijo',
            'siguiente_numero': 'Siguiente Número',
            'formato': 'Formato',
            'activo': 'Activo',
        }
    
    def clean_formato(self):
        formato = self.cleaned_data.get('formato')
        if formato:
            # Validar que el formato contenga solo ceros
            if not all(c == '0' for c in formato):
                raise ValidationError("El formato debe contener solo ceros (ej: 000000)")
        return formato

class AprobarComprobanteForm(forms.Form):
    """
    Formulario para aprobar comprobantes.
    Incluye validaciones de balance.
    """
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones de aprobación'
        }),
        label="Observaciones"
    )
    
    def __init__(self, *args, **kwargs):
        self.comprobante = kwargs.pop('comprobante', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.comprobante and not self.comprobante.es_balanceado():
            raise ValidationError("El comprobante no está balanceado. No se puede aprobar.")
        
        return cleaned_data
