from django.db import models

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