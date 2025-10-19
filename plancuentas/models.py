# Archivo: plancuentas/models.py
# Descripción: Define el modelo jerárquico de cuentas contables para el Plan de Cuentas.
# Este modelo permite crear una estructura de cuentas con códigos, nombres, tipos y jerarquías.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TipoCuenta(models.TextChoices):
    """
    Opciones para el tipo de cuenta contable.
    Define la clasificación básica de las cuentas según su naturaleza.
    """
    ACTIVO = 'ACTIVO', 'Activo'
    PASIVO = 'PASIVO', 'Pasivo'
    PATRIMONIO = 'PATRIMONIO', 'Patrimonio Neto'
    INGRESO = 'INGRESO', 'Ingreso'
    GASTO = 'GASTO', 'Gasto'
    COSTO = 'COSTO', 'Costo de Venta'

class NaturalezaCuenta(models.TextChoices):
    """
    Opciones para la naturaleza de la cuenta.
    Define si la cuenta aumenta o disminuye con débitos o créditos.
    """
    DEUDORA = 'DEUDORA', 'Deudora'
    ACREEDORA = 'ACREEDORA', 'Acreedora'

class PlanCuentas(models.Model):
    """
    Modelo principal para el Plan de Cuentas contable.
    Representa cada cuenta individual con su código, nombre y características.
    """
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código de Cuenta",
        help_text="Código único de la cuenta (ej: 1.1.01.001)"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Cuenta",
        help_text="Nombre descriptivo de la cuenta"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoCuenta.choices,
        verbose_name="Tipo de Cuenta"
    )
    naturaleza = models.CharField(
        max_length=20,
        choices=NaturalezaCuenta.choices,
        verbose_name="Naturaleza"
    )
    nivel = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nivel",
        help_text="Nivel jerárquico de la cuenta (1-5)"
    )
    cuenta_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cuentas_hijas',
        verbose_name="Cuenta Padre",
        help_text="Cuenta de nivel superior en la jerarquía"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de la cuenta"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Cuenta Activa",
        help_text="Indica si la cuenta está disponible para uso"
    )
    permite_movimiento = models.BooleanField(
        default=True,
        verbose_name="Permite Movimiento",
        help_text="Indica si se pueden registrar movimientos en esta cuenta"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Modificación"
    )
    
    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Plan de Cuentas"
        db_table = "plan_cuentas"
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['nivel']),
            models.Index(fields=['activa']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_codigo_completo(self):
        """
        Retorna el código completo de la cuenta incluyendo la jerarquía.
        """
        return self.codigo
    
    def get_nivel_identacion(self):
        """
        Retorna el nivel de identación para mostrar la jerarquía.
        """
        return (self.nivel - 1) * 4  # 4 espacios por nivel
    
    def es_cuenta_hoja(self):
        """
        Verifica si la cuenta es una cuenta hoja (sin subcuentas).
        """
        return not self.cuentas_hijas.exists()
    
    def get_saldo_inicial(self):
        """
        Retorna el saldo inicial de la cuenta.
        """
        try:
            saldo_inicial = self.saldos_iniciales.first()
            return saldo_inicial.saldo if saldo_inicial else 0
        except:
            return 0
    
    def get_saldo_actual(self):
        """
        Calcula el saldo actual de la cuenta basado en movimientos.
        """
        # Esta función se implementará cuando se creen los comprobantes
        return 0

class SaldoInicial(models.Model):
    """
    Modelo para registrar los saldos iniciales de las cuentas.
    Permite establecer el estado inicial del Plan de Cuentas.
    """
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.CASCADE,
        related_name='saldos_iniciales',
        verbose_name="Cuenta"
    )
    saldo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Saldo Inicial"
    )
    fecha = models.DateField(
        verbose_name="Fecha del Saldo"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    class Meta:
        verbose_name = "Saldo Inicial"
        verbose_name_plural = "Saldos Iniciales"
        db_table = "saldos_iniciales"
        unique_together = ['cuenta', 'fecha']
    
    def __str__(self):
        return f"Saldo inicial de {self.cuenta.codigo} - {self.saldo}"
