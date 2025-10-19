# Archivo: usuario/forms.py
# Descripción: Define los formularios para el módulo de usuario del sistema contable.
# Incluye formularios de login, registro y perfil de usuario.

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import UsuarioContable

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para el login del sistema contable.
    Extiende el formulario de autenticación de Django con estilos personalizados.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        }),
        label="Usuario"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label="Contraseña"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario contable.
    Permite modificar información personal sin cambiar credenciales.
    """
    class Meta:
        model = UsuarioContable
        fields = ['first_name', 'last_name', 'email', 'telefono', 'cargo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'cargo': 'Cargo',
        }

class CambioPasswordForm(forms.Form):
    """
    Formulario para cambiar la contraseña del usuario.
    Incluye validación de contraseña actual y nueva contraseña.
    """
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        }),
        label="Contraseña actual"
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label="Nueva contraseña"
    )
    password_confirmacion = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label="Confirmar nueva contraseña"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
