from django import forms
from .models import Comprobante,DescripcionCuentas

class CreateNewComprobante(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['numero','fecha','glosa','beneficiario','ufv','tipo','imagen']

class InsertNewComprobante2(forms.ModelForm):
    class Meta:
        model = DescripcionCuentas
        fields=['debe','haber']
        widgets = {
            'debe': forms.NumberInput(attrs={
                'id': 'id_debe-i',
                'class': 'form-control'
            }),
            'haber': forms.NumberInput(attrs={
                'id': 'id_haber-i',
                'class': 'form-control'
            }),
        }

class InsertNewComprobante(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields= ['numero','fecha','glosa','beneficiario','tipo','imagen']
        widgets = {
            'numero': forms.NumberInput(attrs={
                'id': 'numeroC',
                'name': 'numeroC',
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'name': 'tipo-i',
                'class': 'form-select'
            }),
            'glosa': forms.TextInput(attrs={
                'name': 'glosa-i',
                'class': 'form-control'
            }),
            'beneficiario': forms.TextInput(attrs={
                'name': 'beneficiario-i',
                'class': 'form-control'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'name': 'imagen-i',
                'class': 'form-control'
            }),
        }

class CreateNewDescripcionCuenta(forms.ModelForm):
    class Meta:
        model = DescripcionCuentas
        fields= ['debe','haber']


    
class EditComprobante(forms.Form):
    glosa= forms.CharField(label="Glosa", max_length=100)
    debe = forms.DecimalField(label="Total Debe", max_digits=12, decimal_places=2)
    haber = forms.DecimalField(label="Total Haber", max_digits=12, decimal_places=2)
    beneficiario = forms.CharField(label="Beneficiario", max_length=100)
    tipocambio = forms.DecimalField(label="Tipo de Cambio", max_digits=2, decimal_places=2)
    ufv = forms.DecimalField(label="UFV", max_digits=10, decimal_places=5)
    responsables = forms.CharField(label="Responsables", max_length=100)
    imagen = forms.ImageField(label="Imagen del Comprobante", required=False)