# Archivo: plancuentas/forms.py
# Descripción: Define los formularios para el módulo de Plan de Cuentas.
# Incluye formularios para crear, editar y buscar cuentas contables.

from django import forms
from django.core.exceptions import ValidationError
from .models import PlanCuentas, SaldoInicial, TipoCuenta, NaturalezaCuenta

class PlanCuentasForm(forms.ModelForm):
    """
    Formulario para crear y editar cuentas del Plan de Cuentas.
    Incluye validaciones específicas para códigos y jerarquías.
    """
    class Meta:
        model = PlanCuentas
        fields = [
            'codigo', 'nombre', 'tipo', 'naturaleza', 'nivel', 
            'cuenta_padre', 'descripcion', 'activa', 'permite_movimiento'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1.1.01.001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la cuenta'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'naturaleza': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'cuenta_padre': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada de la cuenta'
            }),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permite_movimiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo': 'Código de Cuenta',
            'nombre': 'Nombre de la Cuenta',
            'tipo': 'Tipo de Cuenta',
            'naturaleza': 'Naturaleza',
            'nivel': 'Nivel Jerárquico',
            'cuenta_padre': 'Cuenta Padre',
            'descripcion': 'Descripción',
            'activa': 'Cuenta Activa',
            'permite_movimiento': 'Permite Movimiento',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar cuentas padre disponibles
        self.fields['cuenta_padre'].queryset = PlanCuentas.objects.filter(activa=True)
        self.fields['cuenta_padre'].empty_label = "Seleccione una cuenta padre (opcional)"
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Validar formato del código
            if not self._validar_formato_codigo(codigo):
                raise ValidationError(
                    "El código debe tener el formato correcto (ej: 1.1.01.001)"
                )
            
            # Verificar unicidad si es una nueva cuenta
            if not self.instance.pk:
                if PlanCuentas.objects.filter(codigo=codigo).exists():
                    raise ValidationError("Ya existe una cuenta con este código.")
        
        return codigo
    
    def clean_nivel(self):
        nivel = self.cleaned_data.get('nivel')
        cuenta_padre = self.cleaned_data.get('cuenta_padre')
        
        if cuenta_padre and nivel:
            if nivel <= cuenta_padre.nivel:
                raise ValidationError(
                    f"El nivel debe ser mayor al nivel de la cuenta padre ({cuenta_padre.nivel})"
                )
        
        return nivel
    
    def _validar_formato_codigo(self, codigo):
        """
        Valida el formato del código de cuenta.
        Acepta formatos como: 1, 1.1, 1.1.01, 1.1.01.001
        """
        import re
        patron = r'^\d+(\.\d+)*$'
        return bool(re.match(patron, codigo))

class BuscarCuentaForm(forms.Form):
    """
    Formulario para buscar cuentas en el Plan de Cuentas.
    Permite filtrar por diferentes criterios.
    """
    codigo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código'
        }),
        label="Código"
    )
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre'
        }),
        label="Nombre"
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(TipoCuenta.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo"
    )
    naturaleza = forms.ChoiceField(
        choices=[('', 'Todas las naturalezas')] + list(NaturalezaCuenta.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Naturaleza"
    )
    nivel = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '5',
            'placeholder': 'Nivel específico'
        }),
        label="Nivel"
    )
    activa = forms.ChoiceField(
        choices=[
            ('', 'Todas'),
            ('true', 'Solo activas'),
            ('false', 'Solo inactivas')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado"
    )

class SaldoInicialForm(forms.ModelForm):
    """
    Formulario para registrar saldos iniciales de las cuentas.
    Permite establecer el estado inicial del Plan de Cuentas.
    """
    class Meta:
        model = SaldoInicial
        fields = ['cuenta', 'saldo', 'fecha', 'observaciones']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'saldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el saldo inicial'
            }),
        }
        labels = {
            'cuenta': 'Cuenta',
            'saldo': 'Saldo Inicial',
            'fecha': 'Fecha del Saldo',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo cuentas que permiten movimiento
        self.fields['cuenta'].queryset = PlanCuentas.objects.filter(
            activa=True, 
            permite_movimiento=True
        )
        self.fields['cuenta'].empty_label = "Seleccione una cuenta"

class ImportarPlanCuentasForm(forms.Form):
    """
    Formulario para importar un Plan de Cuentas desde archivo.
    Soporta archivos CSV y Excel.
    """
    archivo = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        label="Archivo del Plan de Cuentas",
        help_text="Seleccione un archivo CSV o Excel con el Plan de Cuentas"
    )
    sobrescribir = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Sobrescribir cuentas existentes",
        help_text="Marcar si desea reemplazar cuentas con códigos duplicados"
    )
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar extensión del archivo
            extension = archivo.name.split('.')[-1].lower()
            if extension not in ['csv', 'xlsx', 'xls']:
                raise ValidationError(
                    "El archivo debe ser de tipo CSV, XLSX o XLS"
                )
            
            # Validar tamaño del archivo (máximo 5MB)
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError(
                    "El archivo no puede ser mayor a 5MB"
                )
        
        return archivo
