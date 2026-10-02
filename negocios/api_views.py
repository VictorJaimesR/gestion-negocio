from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.db.models import Sum
from .models import Persona, Inmueble, Venta, Financiamiento, Cuota, Arriendo, ObligacionArriendo, Honorario, Movimiento
from .serializers import PersonaSerializer, InmuebleSerializer, VentaSerializer, FinanciamientoSerializer, CuotaSerializer, ArriendoSerializer, ObligacionArriendoSerializer, HonorarioSerializer, MovimientoSerializer

def eliminar_instancia(instance, mensaje):
    try:
        instance.delete()
    except ProtectedError:
        raise ValidationError({'detail': mensaje})


class EliminacionProtegidaMixin:
    def perform_destroy(self, instance):
        eliminar_instancia(instance, 'No se puede eliminar este registro porque tiene información relacionada.')


class PersonaViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

class InmuebleViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Inmueble.objects.all()
    serializer_class = InmuebleSerializer   

class VentaViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def perform_create(self, serializer):
        venta = serializer.save()
        venta.inmueble.estado = Inmueble.ESTADO_VENDIDO
        venta.inmueble.save(update_fields=['estado'])

    def perform_update(self, serializer):
        venta = serializer.save()
        nuevo_estado = (
            Inmueble.ESTADO_DISPONIBLE
            if venta.estado == Venta.ESTADO_CANCELADA
            else Inmueble.ESTADO_VENDIDO
        )
        if venta.inmueble.estado != nuevo_estado:
            venta.inmueble.estado = nuevo_estado
            venta.inmueble.save(update_fields=['estado'])

    def perform_destroy(self, instance):
        if instance.estado not in [Venta.ESTADO_PAGADA, Venta.ESTADO_CANCELADA]:
            raise ValidationError({'detail': 'Solo se puede eliminar una venta pagada o cancelada.'})
        inmueble = instance.inmueble
        with transaction.atomic():
            financiamiento = getattr(instance, 'financiamiento', None)
            if financiamiento:
                cuotas = list(financiamiento.cuotas.all())
                Movimiento.objects.filter(cuota__in=cuotas).delete()
                Cuota.objects.filter(financiamiento=financiamiento).delete()
                financiamiento.delete()
            eliminar_instancia(instance, 'No se puede eliminar la venta porque tiene información relacionada.')
        if not Venta.objects.filter(
            inmueble=inmueble,
            estado__in=[Venta.ESTADO_ACTIVA, Venta.ESTADO_PAGADA],
        ).exists():
            inmueble.estado = Inmueble.ESTADO_DISPONIBLE
            inmueble.save(update_fields=['estado'])

class FinanciamientoViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Financiamiento.objects.all()
    serializer_class = FinanciamientoSerializer

class CuotaViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

class ArriendoViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Arriendo.objects.all()
    serializer_class = ArriendoSerializer

    def perform_create(self, serializer):
        arriendo = serializer.save()
        nuevo_estado = (
            Inmueble.ESTADO_ARRENDADO
            if arriendo.estado == Arriendo.ESTADO_ACTIVO
            else Inmueble.ESTADO_DISPONIBLE
        )
        arriendo.inmueble.estado = nuevo_estado
        arriendo.inmueble.save(update_fields=['estado'])

    def perform_update(self, serializer):
        inmueble_anterior = serializer.instance.inmueble
        arriendo = serializer.save()

        if inmueble_anterior.pk != arriendo.inmueble.pk:
            inmueble_anterior.estado = Inmueble.ESTADO_DISPONIBLE
            inmueble_anterior.save(update_fields=['estado'])

        nuevo_estado = (
            Inmueble.ESTADO_ARRENDADO
            if arriendo.estado == Arriendo.ESTADO_ACTIVO
            else Inmueble.ESTADO_DISPONIBLE
        )
        arriendo.inmueble.estado = nuevo_estado
        arriendo.inmueble.save(update_fields=['estado'])

    def perform_destroy(self, instance):
        if instance.estado != Arriendo.ESTADO_FINALIZADO:
            raise ValidationError({'detail': 'Solo se puede eliminar un arriendo finalizado.'})
        inmueble = instance.inmueble
        with transaction.atomic():
            obligaciones = list(instance.obligaciones.all())
            Movimiento.objects.filter(obligacion_arriendo__in=obligaciones).delete()
            ObligacionArriendo.objects.filter(arriendo=instance).delete()
            eliminar_instancia(instance, 'No se puede eliminar el arriendo porque tiene información relacionada.')
        if not Arriendo.objects.filter(
            inmueble=inmueble,
            estado=Arriendo.ESTADO_ACTIVO,
        ).exists():
            inmueble.estado = Inmueble.ESTADO_DISPONIBLE
            inmueble.save(update_fields=['estado'])

class ObligacionArriendoViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = ObligacionArriendo.objects.all()
    serializer_class = ObligacionArriendoSerializer 

class HonorarioViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Honorario.objects.all()
    serializer_class = HonorarioSerializer

class MovimientoViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer

@api_view(['GET'])
def cuentas_por_cobrar(request):
    total_ventas = Cuota.objects.filter(
        estado__in = ['pendiente', 'parcialmente_pagada']
    ).aggregate(total=Sum('valor_cuota'))['total'] or 0

    total_arriendos = ObligacionArriendo.objects.filter(
        estado__in = ['pendiente', 'parcialmente_pagada']
    ).aggregate(total=Sum('valor_obligacion'))['total'] or 0

    total_honorarios = Honorario.objects.filter(
        estado__in = ['pendiente', 'parcialmente_pagada']
    ).aggregate(total=Sum('valor_honorario'))['total'] or 0

    data = {

        'total_ventas': total_ventas,
        'total_arriendos': total_arriendos,
        'total_honorarios': total_honorarios,
        'total_general': total_ventas + total_arriendos + total_honorarios,
    }
    return Response(data)