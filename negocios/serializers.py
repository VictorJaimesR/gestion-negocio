from rest_framework import serializers
from .models import Cuota, Financiamiento, Inmueble, Persona, Venta, Arriendo, ObligacionArriendo, Honorario, Movimiento

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class InmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inmueble
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'

class FinanciamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Financiamiento
        fields = '__all__'

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

class ArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arriendo
        fields = '__all__'

class ObligacionArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligacionArriendo
        fields = '__all__'

class HonorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honorario
        fields = '__all__'

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'



