# Archivo: comprobantes/models.py
# Descripción: Define los modelos para el módulo de comprobantes contables.
# Incluye comprobantes, detalles de comprobantes y tipos de comprobantes.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from plancuentas.models import PlanCuentas

User = get_user_model()

class TipoComprobante(models.TextChoices):
    """
    Opciones para el tipo de comprobante contable.
    Define los diferentes tipos de documentos contables.
    """
    INGRESO = 'INGRESO', 'Comprobante de Ingreso'
    EGRESO = 'EGRESO', 'Comprobante de Egreso'
    DIARIO = 'DIARIO', 'Asiento de Diario'
    TRASPASO = 'TRASPASO', 'Asiento de Traspaso'
    AJUSTE = 'AJUSTE', 'Asiento de Ajuste'

class EstadoComprobante(models.TextChoices):
    """
    Opciones para el estado del comprobante.
    Controla el flujo de trabajo de los comprobantes.
    """
    BORRADOR = 'BORRADOR', 'Borrador'
    PENDIENTE = 'PENDIENTE', 'Pendiente de Aprobación'
    APROBADO = 'APROBADO', 'Aprobado'
    ANULADO = 'ANULADO', 'Anulado'

class Comprobante(models.Model):
    """
    Modelo principal para los comprobantes contables.
    Representa cada documento contable con su información básica.
    """
    numero = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Comprobante",
        help_text="Número único del comprobante"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoComprobante.choices,
        verbose_name="Tipo de Comprobante"
    )
    fecha = models.DateField(
        verbose_name="Fecha del Comprobante"
    )
    concepto = models.TextField(
        verbose_name="Concepto",
        help_text="Descripción del comprobante"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoComprobante.choices,
        default=EstadoComprobante.BORRADOR,
        verbose_name="Estado"
    )
    total_debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Debe"
    )
    total_haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Haber"
    )
    referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Referencia",
        help_text="Número de referencia externa"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    usuario_creacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='comprobantes_creados',
        verbose_name="Usuario Creación"
    )
    usuario_aprobacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='comprobantes_aprobados',
        blank=True,
        null=True,
        verbose_name="Usuario Aprobación"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Modificación"
    )
    fecha_aprobacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Aprobación"
    )
    
    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        db_table = "comprobantes"
        ordering = ['-fecha', '-numero']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['tipo']),
            models.Index(fields=['fecha']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.numero} - {self.fecha}"
    
    def es_balanceado(self):
        """
        Verifica si el comprobante está balanceado (debe = haber).
        """
        return self.total_debe == self.total_haber
    
    def calcular_totales(self):
        """
        Calcula los totales de debe y haber del comprobante.
        """
        detalles = self.detalles.all()
        self.total_debe = sum(detalle.debe for detalle in detalles)
        self.total_haber = sum(detalle.haber for detalle in detalles)
        self.save(update_fields=['total_debe', 'total_haber'])
    
    def aprobar(self, usuario):
        """
        Aprueba el comprobante.
        """
        if self.estado == EstadoComprobante.BORRADOR:
            self.estado = EstadoComprobante.APROBADO
            self.usuario_aprobacion = usuario
            self.fecha_aprobacion = models.DateTimeField(auto_now=True)
            self.save()
            return True
        return False
    
    def anular(self, usuario):
        """
        Anula el comprobante.
        """
        if self.estado in [EstadoComprobante.BORRADOR, EstadoComprobante.PENDIENTE]:
            self.estado = EstadoComprobante.ANULADO
            self.save()
            return True
        return False

class DetalleComprobante(models.Model):
    """
    Modelo para los detalles de cada comprobante.
    Representa cada línea de débito o crédito del comprobante.
    """
    comprobante = models.ForeignKey(
        Comprobante,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Comprobante"
    )
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.PROTECT,
        verbose_name="Cuenta Contable"
    )
    concepto = models.CharField(
        max_length=200,
        verbose_name="Concepto del Movimiento"
    )
    debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Debe"
    )
    haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Haber"
    )
    orden = models.PositiveIntegerField(
        verbose_name="Orden",
        help_text="Orden de aparición en el comprobante"
    )
    
    class Meta:
        verbose_name = "Detalle de Comprobante"
        verbose_name_plural = "Detalles de Comprobantes"
        db_table = "detalles_comprobantes"
        ordering = ['comprobante', 'orden']
        indexes = [
            models.Index(fields=['comprobante']),
            models.Index(fields=['cuenta']),
        ]
    
    def __str__(self):
        return f"{self.comprobante.numero} - {self.cuenta.codigo} - {self.concepto}"
    
    def clean(self):
        """
        Validación personalizada del detalle.
        """
        from django.core.exceptions import ValidationError
        
        # Verificar que no se tenga debe y haber al mismo tiempo
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("No se puede tener debe y haber al mismo tiempo.")
        
        # Verificar que al menos uno sea mayor a 0
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("Debe o haber debe ser mayor a 0.")
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para validaciones y actualizar totales.
        """
        self.clean()
        super().save(*args, **kwargs)
        # Actualizar totales del comprobante
        self.comprobante.calcular_totales()

class SecuenciaComprobante(models.Model):
    """
    Modelo para manejar la secuencia de numeración de comprobantes.
    Permite diferentes secuencias por tipo de comprobante.
    """
    tipo = models.CharField(
        max_length=20,
        choices=TipoComprobante.choices,
        unique=True,
        verbose_name="Tipo de Comprobante"
    )
    prefijo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Prefijo",
        help_text="Prefijo para el número (ej: CI, CE, AD)"
    )
    siguiente_numero = models.PositiveIntegerField(
        default=1,
        verbose_name="Siguiente Número"
    )
    formato = models.CharField(
        max_length=20,
        default="000000",
        verbose_name="Formato",
        help_text="Formato del número (ej: 000000 para 6 dígitos)"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = "Secuencia de Comprobante"
        verbose_name_plural = "Secuencias de Comprobantes"
        db_table = "secuencias_comprobantes"
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.siguiente_numero}"
    
    def obtener_siguiente_numero(self):
        """
        Obtiene el siguiente número en la secuencia.
        """
        numero = self.siguiente_numero
        self.siguiente_numero += 1
        self.save()
        return numero
    
    def formatear_numero(self, numero):
        """
        Formatea el número según el formato configurado.
        """
        return f"{self.prefijo or ''}{numero:0{len(self.formato)}d}"
