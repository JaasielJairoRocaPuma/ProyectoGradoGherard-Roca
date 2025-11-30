from django.db import models
from django.db.models import F
from plancuentas.models import CuentaAuxiliar
# Create your models here.

class Extencion(models.TextChoices):
    LP = 'LP', 'La Paz'
    CB = 'CB', 'Cochabamba'
    SC = 'SC', 'Santa Cruz'
    OR = 'OR', 'Oruro'
    PT = 'PT', 'Potosi'
    TJ = 'TJ', 'Tarija'
    CH = 'CH', 'Chuquisaca'
    BE = 'BE', 'Beni'
    PD = 'PD', 'Pando'

class Firmas(models.Model):
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    ci=models.CharField(max_length=20, unique=True)
    extencion= models.CharField(max_length=2, choices=Extencion.choices)
    def __str__(self):
        return f"{self.nombre} - {self.cargo}"

class DescripcionCuentas(models.Model):
    cuenta = models.ForeignKey(CuentaAuxiliar, on_delete=models.CASCADE)
    debe = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    haber = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    def __str__(self):
        return f"{self.cuenta.codigo} - {self.cuenta.nombre} | Debe: {self.debe} | Haber: {self.haber}"

class TipoComprobante(models.IntegerChoices):
    DIARIO = 1, 'Diario'
    INGRESO = 2, 'Ingreso'
    EGRESO = 3, 'Egreso'
    AJUSTE = 4, 'Ajuste'

    def __str__(self):
        return self.label


class Comprobante(models.Model):
    numero = models.IntegerField(blank=True,null=True)
    fecha = models.DateField()
    glosa = models.CharField(max_length=100)
    descripcionCuentas = models.ManyToManyField(DescripcionCuentas)  # referencia a otro modelo
    beneficiario = models.CharField(max_length=100)
    tipocambio = models.DecimalField(max_digits=10, decimal_places=4)  # ajusté max_digits
    ufv = models.DecimalField(max_digits=12, decimal_places=6)
    responsables = models.ManyToManyField(Firmas, related_name='responsables')
    tipo = models.IntegerField(choices=TipoComprobante.choices, default=TipoComprobante.DIARIO)
    imagen = models.ImageField(upload_to='comprobantes/', blank=True, null=True)

    

    def __str__(self):
        return f"Comprobante Nro:{self.numero} - {self.get_tipo_display()}"
    
    def agregar(self, *args, **kwargs):
        """
        Agrega un comprobante al final de la lista según su tipo.
        """
        ultimo = Comprobante.objects.filter(tipo=self.tipo).order_by('-numero').first()
        if ultimo:
            self.numero = ultimo.numero + 1
        else:
            self.numero = 1
        self.save()
        # Agregar las cuentas asociadas (ManyToMany)
        cuentas = kwargs.get('cuentas', [])
        for c in cuentas:
            self.descripcionCuentas.add(c)
        # Agregar los responsables (ManyToMany)
        firmas = kwargs.get('firmas', [])    
        for f in firmas:
            self.responsables.add(f)
        return self

    @classmethod
    def insertar(cls, posicion, glosa, fecha, beneficiario, tipocambio, ufv, tipo, **kwargs):
        """
        Inserta un comprobante en la posición indicada (reordena los existentes)
        y asigna las cuentas y responsables relacionados correctamente.
        """
        # Mover los comprobantes que tengan un número >= a la posición
        cls.objects.filter(tipo=tipo, numero__gte=posicion).update(numero=F('numero') + 1)

        # Crear el nuevo comprobante
        nuevo = cls.objects.create(
            numero=posicion,
            glosa=glosa,
            fecha=fecha,
            beneficiario=beneficiario,
            tipocambio=tipocambio,
            ufv=ufv,
            tipo=tipo
        )

        # Agregar las cuentas asociadas (ManyToMany)
        cuentas = kwargs.get('cuentas', [])
        for c in cuentas:
            nuevo.descripcionCuentas.add(c)

        # Agregar los responsables (ManyToMany)
        firmas = kwargs.get('firmas', [])    
        for f in firmas:
            nuevo.responsables.add(f)

        return nuevo

    def eliminar(self):
        """
        Elimina el comprobante y reordena los números de los comprobantes restantes.
        """
        tipo = self.tipo
        numero = self.numero
        self.delete()
        # Reordenar los comprobantes restantes
        Comprobante.objects.filter(tipo=tipo, numero__gt=numero).update(numero=F('numero') - 1)
