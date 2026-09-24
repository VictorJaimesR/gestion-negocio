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

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

class FinanciamientoSerializer(serializers.ModelSerializer):
    cuotas = CuotaSerializer(many=True, read_only=True)
    capital_financiado = serializers.ReadOnlyField()
    class Meta:
        model = Financiamiento
        fields = ['id', 'venta', 'pago_inicial', 'numero_cuotas','valor_cuota', 'capital_financiado', 'cuotas']

class VentaSerializer(serializers.ModelSerializer):
    inmueble = serializers.StringRelatedField()
    comprador = serializers.StringRelatedField()
    financiamiento = FinanciamientoSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = '__all__'

class ObligacionArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligacionArriendo
        fields = '__all__'

class ArriendoSerializer(serializers.ModelSerializer):
    inmueble = serializers.StringRelatedField()
    arrendatario = serializers.StringRelatedField()
    obligaciones = ObligacionArriendoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Arriendo
        fields = '__all__'

class HonorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honorario
        fields = '__all__'

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'



