from rest_framework import serializers
from .models import Cuota, Financiamiento, Inmueble, Persona, Venta, Arriendo, ObligacionArriendo, Honorario, Movimiento

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class InmuebleSerializer(serializers.ModelSerializer):
    descripcion = serializers.CharField(validators=[])

    class Meta:
        model = Inmueble
        fields = '__all__'

    def validate_descripcion(self, descripcion):
        descripcion = descripcion.strip()
        inmuebles = Inmueble.objects.filter(descripcion=descripcion)
        if self.instance:
            inmuebles = inmuebles.exclude(pk=self.instance.pk)
        if inmuebles.exists():
            raise serializers.ValidationError('descripcion no permitida')
        return descripcion

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
    inmueble = serializers.PrimaryKeyRelatedField(queryset=Inmueble.objects.all())
    comprador = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())
    financiamiento = FinanciamientoSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = '__all__'

    def validate_inmueble(self, inmueble):
        ventas_activas = Venta.objects.filter(
            inmueble=inmueble,
            estado__in=[Venta.ESTADO_ACTIVA, Venta.ESTADO_PAGADA],
        )
        if self.instance:
            ventas_activas = ventas_activas.exclude(pk=self.instance.pk)
        if ventas_activas.exists():
            raise serializers.ValidationError(
                'Este inmueble ya tiene una venta activa o pagada.'
            )
        return inmueble

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['inmueble'] = str(instance.inmueble)
        data['comprador'] = str(instance.comprador)
        data['inmueble_id'] = instance.inmueble_id
        data['comprador_id'] = instance.comprador_id
        return data

class ObligacionArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligacionArriendo
        fields = '__all__'

class ArriendoSerializer(serializers.ModelSerializer):
    inmueble = serializers.PrimaryKeyRelatedField(queryset=Inmueble.objects.all())
    arrendatario = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())
    obligaciones = ObligacionArriendoSerializer(many=True, read_only=True)

    class Meta:
        model = Arriendo
        fields = '__all__'

    def validate_inmueble(self, inmueble):
        if inmueble.estado == Inmueble.ESTADO_VENDIDO:
            raise serializers.ValidationError(
                'Este inmueble está vendido y no se puede arrendar.'
            )
        arriendos_activos = Arriendo.objects.filter(
            inmueble=inmueble,
            estado=Arriendo.ESTADO_ACTIVO,
        )
        if self.instance:
            arriendos_activos = arriendos_activos.exclude(pk=self.instance.pk)
        if arriendos_activos.exists():
            raise serializers.ValidationError(
                'Este inmueble ya tiene un arriendo activo.'
            )
        return inmueble

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['inmueble'] = str(instance.inmueble)
        data['arrendatario'] = str(instance.arrendatario)
        data['inmueble_id'] = instance.inmueble_id
        data['arrendatario_id'] = instance.arrendatario_id
        return data

class HonorarioSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())

    class Meta:
        model = Honorario
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cliente'] = str(instance.cliente)
        data['cliente_id'] = instance.cliente_id
        return data

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'



