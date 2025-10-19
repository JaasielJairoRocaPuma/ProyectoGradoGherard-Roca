# Archivo: usuario/admin.py
# Descripción: Configuración del panel de administración para el módulo de usuario.
# Permite gestionar usuarios contables desde el admin de Django.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioContable

@admin.register(UsuarioContable)
class UsuarioContableAdmin(UserAdmin):
    """
    Configuración personalizada del admin para UsuarioContable.
    Extiende la configuración base de UserAdmin con campos adicionales.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'cargo', 'activo', 'date_joined')
    list_filter = ('activo', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cargo')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'cargo')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_creacion')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email'),
        }),
    )
    
    readonly_fields = ('date_joined', 'fecha_creacion', 'last_login')
