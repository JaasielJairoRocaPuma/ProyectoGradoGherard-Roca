from django import forms

class CreateNewCuentaAuxiliar(forms.Form):
    cod= forms.IntegerField(label="Código de la cuenta")
    nombre = forms.CharField(label="Titulo de la cuenta", max_length=200)

class EditCuentaAuxiliar(forms.Form):
    nombre = forms.CharField(label="Titulo de la cuenta", max_length=200)
