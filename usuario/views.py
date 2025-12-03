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
from django.db.models import Sum, F
from .forms import LoginForm, PerfilUsuarioForm, CambioPasswordForm
from .models import UsuarioContable
from comprobantes.models import DescripcionCuentas
from plancuentas.models import CuentaAuxiliar
import google.generativeai as genai

GEN_API_KEY="AIzaSyAnrMV2Z0Zn9FT0sZeOD5WrlqQsTYPBi2A"
genai.configure(api_key=GEN_API_KEY)

class LoginView(TemplateView):
    """
    Vista para el login del sistema contable.
    Maneja la autenticación del usuario único del sistema.
    """
    template_name = 'usuario/login.html'
    
    def get(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('usuario:dashboard')
        
        form = LoginForm(request=request)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request=request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.activo:
                    login(request, user)
                    messages.success(request, f'Bienvenido, {user.get_full_name()}')
                    return redirect('usuario:dashboard')
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
    return redirect('usuario:login')

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

@login_required
def datos_grafico_cuentas(request):
    """
    Vista AJAX que devuelve los datos agregados de todas las cuentas de nivel 5
    para el gráfico de pastel en el resumen financiero.
    """
    # Obtener todas las cuentas de nivel 5 (CuentaAuxiliar)
    cuentas_nivel5 = CuentaAuxiliar.objects.all()
    
    datos_grafico = []
    for cuenta in cuentas_nivel5:
        # Sumar debe y haber de todas las DescripcionCuentas relacionadas
        totales = DescripcionCuentas.objects.filter(cuenta=cuenta).aggregate(
            total_debe=Sum('debe') or 0,
            total_haber=Sum('haber') or 0
        )
        
        # Calcular saldo (debe - haber)
        saldo = (totales['total_debe'] or 0) - (totales['total_haber'] or 0)
        
        # Solo incluir si tiene movimiento
        if saldo != 0:
            datos_grafico.append({
                'nombre': cuenta.nombre,
                'codigo': cuenta.codigo,
                'saldo': float(abs(saldo)),  # Valor absoluto para el gráfico
                'saldo_real': float(saldo)  # Saldo real para detectar negativos
            })
    
    return JsonResponse({'cuentas': datos_grafico})

@login_required
def alertas_cuentas_rojo(request):
    """
    Vista AJAX que detecta cuentas con saldo negativo (en rojo) y genera
    mensajes descriptivos usando la API de Gemini.
    """
    cuentas_nivel5 = CuentaAuxiliar.objects.all()
    cuentas_en_rojo = []
    
    for cuenta in cuentas_nivel5:
        # Sumar debe y haber de todas las DescripcionCuentas relacionadas
        totales = DescripcionCuentas.objects.filter(cuenta=cuenta).aggregate(
            total_debe=Sum('debe') or 0,
            total_haber=Sum('haber') or 0
        )
        
        # Calcular saldo (debe - haber)
        saldo = (totales['total_debe'] or 0) - (totales['total_haber'] or 0)
        
        # Si el saldo es negativo, está en rojo
        if saldo < 0:
            cuentas_en_rojo.append({
                'codigo': cuenta.codigo,
                'nombre': cuenta.nombre,
                'saldo': float(saldo),
                'saldo_absoluto': float(abs(saldo))
            })
    
    # Si hay cuentas en rojo, usar Gemini para generar mensaje descriptivo
    mensaje_alerta = ""
    if cuentas_en_rojo:
        try:
            # Crear un resumen de las cuentas en rojo
            resumen_cuentas = "\n".join([
                f"- {c['codigo']} {c['nombre']}: Saldo negativo de {c['saldo_absoluto']:,.2f}"
                for c in cuentas_en_rojo[:5]  # Primeras 5 para no saturar
            ])
            
            prompt = f"""Como experto contable, analiza las siguientes cuentas que tienen saldo negativo (en rojo):
            
{resumen_cuentas}

Genera un mensaje breve y profesional (máximo 150 palabras) en español que:
1. Alerte sobre la situación
2. Explique brevemente qué significa tener cuentas en rojo
3. Sugiera acciones básicas a considerar

Responde SOLO con el mensaje, sin formato adicional."""

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            mensaje_alerta = response.text.strip()
        except Exception as e:
            # Si falla Gemini, usar mensaje predeterminado
            mensaje_alerta = f"⚠️ Alerta: Se detectaron {len(cuentas_en_rojo)} cuenta(s) con saldo negativo. Revise las cuentas contables para corregir los desbalances."
    
    return JsonResponse({
        'tiene_alertas': len(cuentas_en_rojo) > 0,
        'cantidad': len(cuentas_en_rojo),
        'cuentas': cuentas_en_rojo,
        'mensaje': mensaje_alerta
    })
