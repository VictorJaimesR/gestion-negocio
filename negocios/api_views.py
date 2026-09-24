from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Sum
from .models import Persona, Inmueble, Venta, Financiamiento, Cuota, Arriendo, ObligacionArriendo, Honorario, Movimiento
from .serializers import PersonaSerializer, InmuebleSerializer, VentaSerializer, FinanciamientoSerializer, CuotaSerializer, ArriendoSerializer, ObligacionArriendoSerializer, HonorarioSerializer, MovimientoSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

class InmuebleViewSet(viewsets.ModelViewSet):
    queryset = Inmueble.objects.all()
    serializer_class = InmuebleSerializer   

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class FinanciamientoViewSet(viewsets.ModelViewSet):
    queryset = Financiamiento.objects.all()
    serializer_class = FinanciamientoSerializer

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

class ArriendoViewSet(viewsets.ModelViewSet):
    queryset = Arriendo.objects.all()
    serializer_class = ArriendoSerializer

class ObligacionArriendoViewSet(viewsets.ModelViewSet):
    queryset = ObligacionArriendo.objects.all()
    serializer_class = ObligacionArriendoSerializer 

class HonorarioViewSet(viewsets.ModelViewSet):
    queryset = Honorario.objects.all()
    serializer_class = HonorarioSerializer

class MovimientoViewSet(viewsets.ModelViewSet):
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