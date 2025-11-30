# Archivo: plancuentas/models.py
# Descripción: Define el modelo jerárquico de cuentas contables para el Plan de Cuentas.
# Este modelo permite crear una estructura de cuentas con códigos, nombres, tipos y jerarquías.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Grupo(models.Model):
    nombre=models.CharField(max_length=15, unique=True)
    tipo=models.CharField(max_length=10)
    nivel = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(1)],
        editable=False
    )
    def __str__(self):
        return self.nombre
    @property
    def codigo(self):
        return str(self.id)

class SubGrupo(models.Model):
    cod=models.PositiveIntegerField()
    nombre=models.CharField(max_length=100)
    grupo=models.ForeignKey(Grupo, on_delete=models.CASCADE)
    tipo=models.CharField(max_length=10)
    nivel = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(2), MaxValueValidator(2)],
        editable=False
    )
    def __str__(self):
       return self.nombre
    @property
    def codigo(self):
        return f"{self.grupo.id}{self.cod}"

class CuentaMatriz(models.Model):
    cod=models.PositiveIntegerField()
    nombre=models.CharField(max_length=100)
    subgrupo=models.ForeignKey(SubGrupo, on_delete=models.CASCADE)
    tipo=models.CharField(max_length=10)
    nivel = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(3), MaxValueValidator(3)],
        editable=False
    )

    def __str__(self):
        return self.nombre
    @property
    def codigo(self):
        if self.cod < 10:
            return f"{self.subgrupo.grupo.id}{self.subgrupo.cod}0{self.cod}"
        else:
            return f"{self.subgrupo.grupo.id}{self.subgrupo.cod}{self.cod}"

class CuentaMayor(models.Model):
    cod=models.PositiveIntegerField()
    nombre=models.CharField(max_length=100, unique=True)
    cuentamatriz=models.ForeignKey(CuentaMatriz, on_delete=models.CASCADE)
    tipo=models.CharField(max_length=10)
    nivel = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(4), MaxValueValidator(4)],
        editable=False
    )

    def __str__(self):
        return self.nombre
    @property
    def codigo(self):
        if self.cod < 10:
            return f"{self.cuentamatriz.codigo}00{self.cod}"
        elif self.cod >= 10:
            return f"{self.cuentamatriz.codigo}0{self.cod}"

class CuentaAuxiliar(models.Model):
    cod=models.PositiveIntegerField()
    nombre=models.CharField(max_length=100, unique=True)
    cuentamayor=models.ForeignKey(CuentaMayor, on_delete=models.CASCADE)
    tipo=models.CharField(max_length=10)
    nivel = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(5), MaxValueValidator(5)],
        editable=False
    )

    def __str__(self):
        return self.nombre
    @property
    def codigo(self):
        if self.cod < 10:
            return f"{self.cuentamayor.codigo}00{self.cod}"
        else:
            return f"{self.cuentamayor.codigo}0{self.cod}"

        

