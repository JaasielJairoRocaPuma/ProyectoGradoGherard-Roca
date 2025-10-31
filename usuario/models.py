from django.db import models
from django.contrib.auth.models import AbstractUser

# Archivo: usuario/models.py
# Descripción: Define el modelo de usuario personalizado para el sistema contable.
# Este modelo extiende el usuario base de Django para incluir campos específicos del sistema.

class UsuarioContable(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema contable.
    Extiende el modelo User de Django para incluir campos específicos.
    """
    # Campos adicionales específicos del sistema contable
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name="Teléfono"
    )
    cargo = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Cargo"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Usuario activo"
    )
    
    class Meta:
        verbose_name = "Usuario Contable"
        verbose_name_plural = "Usuarios Contables"
        db_table = "usuario_contable"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
