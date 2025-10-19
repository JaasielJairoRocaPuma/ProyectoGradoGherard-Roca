# Archivo: usuario/views.py
# Descripción: Define las vistas para el módulo de usuario del sistema contable.
# Incluye vistas de login, logout, perfil y gestión de usuario único.

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from .forms import LoginForm, PerfilUsuarioForm, CambioPasswordForm
from .models import UsuarioContable

class LoginView(TemplateView):
    """
    Vista para el login del sistema contable.
    Maneja la autenticación del usuario único del sistema.
    """
    template_name = 'usuario/login.html'
    
    def get(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.activo:
                    login(request, user)
                    messages.success(request, f'Bienvenido, {user.get_full_name()}')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Su cuenta está desactivada.')
            else:
                messages.error(request, 'Credenciales inválidas.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
        
        return render(request, self.template_name, {'form': form})

@login_required
def logout_view(request):
    """
    Vista para cerrar sesión del usuario.
    Limpia la sesión y redirige al login.
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del dashboard del sistema contable.
    Muestra información general y acceso a los módulos principales.
    """
    template_name = 'usuario/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context

@login_required
def perfil_usuario(request):
    """
    Vista para mostrar y editar el perfil del usuario.
    Permite modificar información personal del usuario contable.
    """
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_usuario')
    else:
        form = PerfilUsuarioForm(instance=request.user)
    
    return render(request, 'usuario/perfil.html', {'form': form})

@login_required
def cambiar_password(request):
    """
    Vista para cambiar la contraseña del usuario.
    Incluye validación de contraseña actual y nueva.
    """
    if request.method == 'POST':
        form = CambioPasswordForm(request.POST)
        if form.is_valid():
            password_actual = form.cleaned_data['password_actual']
            password_nueva = form.cleaned_data['password_nueva']
            
            # Verificar contraseña actual
            if request.user.check_password(password_actual):
                request.user.set_password(password_nueva)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('perfil_usuario')
            else:
                messages.error(request, 'La contraseña actual es incorrecta.')
    else:
        form = CambioPasswordForm()
    
    return render(request, 'usuario/cambiar_password.html', {'form': form})

@login_required
def verificar_sesion(request):
    """
    Vista AJAX para verificar el estado de la sesión.
    Útil para mantener la sesión activa en el frontend.
    """
    return JsonResponse({
        'autenticado': request.user.is_authenticated,
        'usuario': request.user.username if request.user.is_authenticated else None
    })
