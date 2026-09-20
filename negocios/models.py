from django.db import models
from dateutil.relativedelta import relativedelta


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre

class Inmueble(models.Model):
    TIPO_VEHICULO = 'vehiculo'
    TIPO_APARTAMENTO = 'apartamento'
    TIPO_CASA = 'casa'
    TIPO_MOTOCICLETA = 'motocicleta'
    TIPO_LOTE = 'lote'
    TIPO_OTRO = 'otro'
    TIPO_CHOICES = [
        (TIPO_VEHICULO, 'Vehículo'),
        (TIPO_APARTAMENTO, 'Apartamento'),
        (TIPO_CASA, 'Casa'),
        (TIPO_MOTOCICLETA, 'Motocicleta'),
        (TIPO_LOTE, 'Lote'),
        (TIPO_OTRO, 'Otro'),
    ]

    ESTADO_DISPONIBLE = 'disponible'
    ESTADO_VENDIDO = 'vendido'
    ESTADO_ARRENDADO = 'arrendado'
    ESTADO_CHOICES = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_VENDIDO, 'Vendido'),
        (ESTADO_ARRENDADO, 'Arrendado'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_DISPONIBLE)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descripcion}"

class Venta(models.Model):
    ESTADO_ACTIVA = 'activa'
    ESTADO_PAGADA = 'pagada'
    ESTADO_CANCELADA = 'cancelada'
    
    ESTADO_CHOICES = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_PAGADA, 'Pagada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]
    
    inmueble = models.ForeignKey(Inmueble, on_delete=models.PROTECT, related_name='ventas')
    comprador = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='compras')
    fecha_venta = models.DateField()
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ACTIVA)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.inmueble} - {self.comprador.nombre} - {self.fecha_venta}"


class Financiamiento(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.PROTECT, related_name='financiamiento')
    pago_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    numero_cuotas = models.PositiveIntegerField()
    valor_cuota = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_inicio = models.DateField()

    @property
    def capital_financiado(self):
        return self.venta.precio_venta - self.pago_inicial

    def generar_cuotas(self):
        for i in range(1, self.numero_cuotas + 1):
            fecha_cuota = self.fecha_inicio + relativedelta(months=i-1)
            Cuota.objects.create(
                financiamiento=self,
                numero_cuota=i,
                fecha_vencimiento=fecha_cuota,
                valor_cuota=self.valor_cuota
            )

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)
        if es_nuevo:
            self.generar_cuotas() 

    def __str__(self):
        return f"Financiamiento de {self.venta}"

class Cuota(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_PARCIALMENTE_PAGADA = 'parcialmente_pagada'
    ESTADO_PAGADA = 'pagada'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PARCIALMENTE_PAGADA, 'Parcialmente Pagada'),
        (ESTADO_PAGADA, 'Pagada'),
    ]

    financiamiento = models.ForeignKey(Financiamiento, on_delete=models.PROTECT, related_name='cuotas')
    numero_cuota = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField()
    valor_cuota = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    class Meta:
        unique_together = ['financiamiento', 'numero_cuota']

    def __str__(self):
        return f"{self.financiamiento} - Cuota #{self.numero_cuota}"
    