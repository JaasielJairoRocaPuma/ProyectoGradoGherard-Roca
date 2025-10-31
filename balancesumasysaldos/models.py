# Archivo: balancesumasysaldos/models.py
# Descripción: Define los modelos para el módulo de Balance de Sumas y Saldos.
# Incluye modelos para reportes contables y análisis de saldos.

from django.db import models
from django.contrib.auth import get_user_model
from plancuentas.models import PlanCuentas
from comprobantes.models import Comprobante, DetalleComprobante
from decimal import Decimal

User = get_user_model()

class BalanceSumasSaldos(models.Model):
    """
    Modelo para almacenar reportes de Balance de Sumas y Saldos.
    Permite generar y guardar reportes para diferentes períodos.
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Reporte",
        help_text="Nombre descriptivo del reporte"
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
    incluir_saldos_cero = models.BooleanField(
        default=False,
        verbose_name="Incluir Saldos Cero",
        help_text="Incluir cuentas con saldo cero en el reporte"
    )
    solo_cuentas_movimiento = models.BooleanField(
        default=True,
        verbose_name="Solo Cuentas con Movimiento",
        help_text="Incluir solo cuentas que tuvieron movimientos en el período"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    class Meta:
        verbose_name = "Balance de Sumas y Saldos"
        verbose_name_plural = "Balances de Sumas y Saldos"
        db_table = "balances_sumas_saldos"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_desde} a {self.fecha_hasta}"
    
    def calcular_totales(self):
        """
        Calcula los totales del balance.
        """
        detalles = self.detalles.all()
        total_debe = sum(detalle.saldo_debe for detalle in detalles)
        total_haber = sum(detalle.saldo_haber for detalle in detalles)
        return total_debe, total_haber
    
    def es_balanceado(self):
        """
        Verifica si el balance está balanceado.
        """
        total_debe, total_haber = self.calcular_totales()
        return total_debe == total_haber

class DetalleBalance(models.Model):
    """
    Modelo para los detalles del Balance de Sumas y Saldos.
    Representa cada línea del reporte con los saldos de las cuentas.
    """
    balance = models.ForeignKey(
        BalanceSumasSaldos,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Balance"
    )
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.PROTECT,
        verbose_name="Cuenta Contable"
    )
    saldo_anterior = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Anterior"
    )
    movimientos_debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Movimientos Debe"
    )
    movimientos_haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Movimientos Haber"
    )
    saldo_debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Debe"
    )
    saldo_haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Haber"
    )
    saldo_final = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Final"
    )
    orden = models.PositiveIntegerField(
        verbose_name="Orden",
        help_text="Orden de aparición en el reporte"
    )
    
    class Meta:
        verbose_name = "Detalle de Balance"
        verbose_name_plural = "Detalles de Balance"
        db_table = "detalles_balance"
        ordering = ['balance', 'orden']
        unique_together = ['balance', 'cuenta']
    
    def __str__(self):
        return f"{self.balance.nombre} - {self.cuenta.codigo}"
    
    def calcular_saldo_final(self):
        """
        Calcula el saldo final de la cuenta.
        """
        if self.cuenta.naturaleza == 'DEUDORA':
            # Para cuentas deudoras: Saldo Anterior + Debe - Haber
            self.saldo_final = self.saldo_anterior + self.movimientos_debe - self.movimientos_haber
        else:
            # Para cuentas acreedoras: Saldo Anterior + Haber - Debe
            self.saldo_final = self.saldo_anterior + self.movimientos_haber - self.movimientos_debe
        
        # Determinar si el saldo final es deudor o acreedor
        if self.saldo_final >= 0:
            if self.cuenta.naturaleza == 'DEUDORA':
                self.saldo_debe = self.saldo_final
                self.saldo_haber = 0
            else:
                self.saldo_debe = 0
                self.saldo_haber = self.saldo_final
        else:
            if self.cuenta.naturaleza == 'DEUDORA':
                self.saldo_debe = 0
                self.saldo_haber = abs(self.saldo_final)
            else:
                self.saldo_debe = abs(self.saldo_final)
                self.saldo_haber = 0
        
        return self.saldo_final

class ConfiguracionBalance(models.Model):
    """
    Modelo para configurar la generación de balances.
    Permite personalizar la forma en que se generan los reportes.
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
    solo_cuentas_movimiento = models.BooleanField(
        default=True,
        verbose_name="Solo Cuentas con Movimiento"
    )
    agrupar_por_tipo = models.BooleanField(
        default=True,
        verbose_name="Agrupar por Tipo de Cuenta"
    )
    mostrar_saldos_anteriores = models.BooleanField(
        default=True,
        verbose_name="Mostrar Saldos Anteriores"
    )
    mostrar_movimientos = models.BooleanField(
        default=True,
        verbose_name="Mostrar Movimientos"
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
        verbose_name = "Configuración de Balance"
        verbose_name_plural = "Configuraciones de Balance"
        db_table = "configuraciones_balance"
    
    def __str__(self):
        return self.nombre

class ResumenBalance(models.Model):
    """
    Modelo para almacenar resúmenes de balances por tipo de cuenta.
    Facilita el análisis rápido de la situación contable.
    """
    balance = models.ForeignKey(
        BalanceSumasSaldos,
        on_delete=models.CASCADE,
        related_name='resumenes',
        verbose_name="Balance"
    )
    tipo_cuenta = models.CharField(
        max_length=20,
        verbose_name="Tipo de Cuenta"
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
    saldo_neto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Neto"
    )
    cantidad_cuentas = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de Cuentas"
    )
    
    class Meta:
        verbose_name = "Resumen de Balance"
        verbose_name_plural = "Resúmenes de Balance"
        db_table = "resumenes_balance"
        unique_together = ['balance', 'tipo_cuenta']
    
    def __str__(self):
        return f"{self.balance.nombre} - {self.tipo_cuenta}"
    
    def calcular_saldo_neto(self):
        """
        Calcula el saldo neto del tipo de cuenta.
        """
        self.saldo_neto = self.total_debe - self.total_haber
        return self.saldo_neto
