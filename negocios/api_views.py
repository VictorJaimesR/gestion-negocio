from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.db.models import Prefetch, Sum
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
    queryset = Venta.objects.select_related(
        'inmueble',
        'comprador',
        'financiamiento',
    ).prefetch_related(
        Prefetch(
            'financiamiento__cuotas',
            queryset=Cuota.objects.prefetch_related('movimientos'),
        ),
    )
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
        financiamiento = getattr(instance, 'financiamiento', None)
        if financiamiento and Movimiento.objects.filter(
            cuota__financiamiento=financiamiento,
        ).exists():
            raise ValidationError({
                'detail': 'No se puede eliminar la venta porque tiene movimientos registrados.'
            })
        inmueble = instance.inmueble
        with transaction.atomic():
            if financiamiento:
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
    queryset = Arriendo.objects.select_related(
        'inmueble',
        'arrendatario',
    ).prefetch_related(
        Prefetch(
            'obligaciones',
            queryset=ObligacionArriendo.objects.prefetch_related('movimientos'),
        ),
    )
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
        if Movimiento.objects.filter(
            obligacion_arriendo__arriendo=instance,
        ).exists():
            raise ValidationError({
                'detail': 'No se puede eliminar el arriendo porque tiene movimientos registrados.'
            })
        inmueble = instance.inmueble
        with transaction.atomic():
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
    queryset = Honorario.objects.select_related('cliente').prefetch_related('movimientos')
    serializer_class = HonorarioSerializer

    def perform_destroy(self, instance):
        if instance.estado != Honorario.ESTADO_PAGADA:
            raise ValidationError({'detail': 'Solo se puede eliminar un honorario pagado.'})
        if Movimiento.objects.filter(honorario=instance).exists():
            raise ValidationError({
                'detail': 'No se puede eliminar el honorario porque tiene movimientos registrados.'
            })
        with transaction.atomic():
            eliminar_instancia(instance, 'No se puede eliminar el honorario porque tiene información relacionada.')

class MovimientoViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Movimiento.objects.select_related(
        'cuota__financiamiento__venta__inmueble',
        'cuota__financiamiento__venta__comprador',
        'obligacion_arriendo__arriendo__inmueble',
        'obligacion_arriendo__arriendo__arrendatario',
        'honorario__cliente',
    )
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