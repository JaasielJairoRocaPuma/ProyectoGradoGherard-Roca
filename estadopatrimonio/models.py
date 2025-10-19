# Archivo: estadopatrimonio/models.py
# Descripción: Define los modelos para el módulo de Estado Patrimonial.
# Incluye modelos para estados financieros y análisis patrimonial.

from django.db import models
from django.contrib.auth import get_user_model
from plancuentas.models import PlanCuentas, TipoCuenta
from comprobantes.models import Comprobante, DetalleComprobante
from decimal import Decimal

User = get_user_model()

class EstadoPatrimonial(models.Model):
    """
    Modelo para almacenar Estados Patrimoniales generados.
    Representa el balance general de la empresa en una fecha específica.
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Estado",
        help_text="Nombre descriptivo del estado patrimonial"
    )
    fecha = models.DateField(
        verbose_name="Fecha del Estado",
        help_text="Fecha de corte del estado patrimonial"
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Generación"
    )
    usuario_generacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuario Generación"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    class Meta:
        verbose_name = "Estado Patrimonial"
        verbose_name_plural = "Estados Patrimoniales"
        db_table = "estados_patrimoniales"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
    
    def calcular_totales(self):
        """
        Calcula los totales del estado patrimonial.
        """
        activos = self.detalles.filter(cuenta__tipo=TipoCuenta.ACTIVO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        pasivos = self.detalles.filter(cuenta__tipo=TipoCuenta.PASIVO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        patrimonio = self.detalles.filter(cuenta__tipo=TipoCuenta.PATRIMONIO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        return activos, pasivos, patrimonio
    
    def es_balanceado(self):
        """
        Verifica si el estado patrimonial está balanceado.
        """
        activos, pasivos, patrimonio = self.calcular_totales()
        return activos == (pasivos + patrimonio)

class DetalleEstadoPatrimonial(models.Model):
    """
    Modelo para los detalles del Estado Patrimonial.
    Representa cada línea del estado con los saldos de las cuentas.
    """
    estado = models.ForeignKey(
        EstadoPatrimonial,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Estado Patrimonial"
    )
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.PROTECT,
        verbose_name="Cuenta Contable"
    )
    saldo_final = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Final"
    )
    orden = models.PositiveIntegerField(
        verbose_name="Orden",
        help_text="Orden de aparición en el estado"
    )
    
    class Meta:
        verbose_name = "Detalle de Estado Patrimonial"
        verbose_name_plural = "Detalles de Estado Patrimonial"
        db_table = "detalles_estado_patrimonial"
        ordering = ['estado', 'orden']
        unique_together = ['estado', 'cuenta']
    
    def __str__(self):
        return f"{self.estado.nombre} - {self.cuenta.codigo}"

class EstadoResultados(models.Model):
    """
    Modelo para almacenar Estados de Resultados generados.
    Representa la utilidad o pérdida del período.
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Estado",
        help_text="Nombre descriptivo del estado de resultados"
    )
    fecha_desde = models.DateField(
        verbose_name="Fecha Desde"
    )
    fecha_hasta = models.DateField(
        verbose_name="Fecha Hasta"
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Generación"
    )
    usuario_generacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuario Generación"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    class Meta:
        verbose_name = "Estado de Resultados"
        verbose_name_plural = "Estados de Resultados"
        db_table = "estados_resultados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_desde} a {self.fecha_hasta}"
    
    def calcular_totales(self):
        """
        Calcula los totales del estado de resultados.
        """
        ingresos = self.detalles.filter(cuenta__tipo=TipoCuenta.INGRESO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        gastos = self.detalles.filter(cuenta__tipo=TipoCuenta.GASTO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        costos = self.detalles.filter(cuenta__tipo=TipoCuenta.COSTO).aggregate(
            total=models.Sum('saldo_final')
        )['total'] or Decimal('0')
        
        utilidad_bruta = ingresos - costos
        utilidad_neta = utilidad_bruta - gastos
        
        return ingresos, gastos, costos, utilidad_bruta, utilidad_neta

class DetalleEstadoResultados(models.Model):
    """
    Modelo para los detalles del Estado de Resultados.
    Representa cada línea del estado con los saldos de las cuentas.
    """
    estado = models.ForeignKey(
        EstadoResultados,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Estado de Resultados"
    )
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.PROTECT,
        verbose_name="Cuenta Contable"
    )
    saldo_final = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Final"
    )
    orden = models.PositiveIntegerField(
        verbose_name="Orden",
        help_text="Orden de aparición en el estado"
    )
    
    class Meta:
        verbose_name = "Detalle de Estado de Resultados"
        verbose_name_plural = "Detalles de Estado de Resultados"
        db_table = "detalles_estado_resultados"
        ordering = ['estado', 'orden']
        unique_together = ['estado', 'cuenta']
    
    def __str__(self):
        return f"{self.estado.nombre} - {self.cuenta.codigo}"

class ConfiguracionEstado(models.Model):
    """
    Modelo para configurar la generación de estados financieros.
    Permite personalizar la forma en que se generan los estados.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de Configuración"
    )
    incluir_saldos_cero = models.BooleanField(
        default=False,
        verbose_name="Incluir Saldos Cero"
    )
    agrupar_por_tipo = models.BooleanField(
        default=True,
        verbose_name="Agrupar por Tipo de Cuenta"
    )
    mostrar_cuentas_principales = models.BooleanField(
        default=True,
        verbose_name="Mostrar Solo Cuentas Principales"
    )
    formato_numero = models.CharField(
        max_length=20,
        default="0,000.00",
        verbose_name="Formato de Números"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Configuración Activa"
    )
    
    class Meta:
        verbose_name = "Configuración de Estado"
        verbose_name_plural = "Configuraciones de Estado"
        db_table = "configuraciones_estado"
    
    def __str__(self):
        return self.nombre

class ResumenFinanciero(models.Model):
    """
    Modelo para almacenar resúmenes financieros.
    Facilita el análisis rápido de la situación financiera.
    """
    estado_patrimonial = models.ForeignKey(
        EstadoPatrimonial,
        on_delete=models.CASCADE,
        related_name='resumenes',
        verbose_name="Estado Patrimonial"
    )
    total_activos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Activos"
    )
    total_pasivos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Pasivos"
    )
    total_patrimonio = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Patrimonio"
    )
    ratio_liquidez = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        verbose_name="Ratio de Liquidez"
    )
    ratio_endeudamiento = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        verbose_name="Ratio de Endeudamiento"
    )
    
    class Meta:
        verbose_name = "Resumen Financiero"
        verbose_name_plural = "Resúmenes Financieros"
        db_table = "resumenes_financieros"
    
    def __str__(self):
        return f"Resumen - {self.estado_patrimonial.nombre}"
    
    def calcular_ratios(self):
        """
        Calcula los ratios financieros.
        """
        if self.total_pasivos > 0:
            self.ratio_liquidez = self.total_activos / self.total_pasivos
            self.ratio_endeudamiento = self.total_pasivos / (self.total_pasivos + self.total_patrimonio)
        else:
            self.ratio_liquidez = Decimal('0')
            self.ratio_endeudamiento = Decimal('0')
        
        return self.ratio_liquidez, self.ratio_endeudamiento
