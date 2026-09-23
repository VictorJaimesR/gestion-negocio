from rest_framework import viewsets
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


