from django import forms
from .models import Comprobante,DescripcionCuentas

class CreateNewComprobante(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['numero','fecha','glosa','beneficiario','ufv','tipo','imagen']

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