from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import Arriendo, Financiamiento, Inmueble, Persona, Venta


class GeneracionPagosTest(TestCase):
    def setUp(self):
        self.persona = Persona.objects.create(
            nombre='Cliente de prueba',
            cedula='TEST-001',
        )
        self.inmueble = Inmueble.objects.create(
            tipo=Inmueble.TIPO_CASA,
            descripcion='Inmueble de prueba',
        )

    def test_arriendo_de_un_mes_crea_una_obligacion(self):
        arriendo = Arriendo.objects.create(
            inmueble=self.inmueble,
            arrendatario=self.persona,
            canon_mensual=Decimal('1000000'),
            fecha_inicio=date(2026, 10, 3),
            fecha_fin=date(2026, 11, 3),
            dia_pago=3,
        )

        self.assertEqual(arriendo.obligaciones.count(), 1)
        self.assertEqual(
            arriendo.obligaciones.get().fecha_vencimiento,
            date(2026, 10, 3),
        )

    def test_arriendo_editado_extiende_obligaciones_sin_duplicarlas(self):
        arriendo = Arriendo.objects.create(
            inmueble=self.inmueble,
            arrendatario=self.persona,
            canon_mensual=Decimal('1000000'),
            fecha_inicio=date(2026, 10, 3),
            fecha_fin=date(2026, 10, 3),
            dia_pago=3,
        )
        arriendo.fecha_fin = date(2027, 1, 3)
        arriendo.save()

        self.assertEqual(arriendo.obligaciones.count(), 3)
        self.assertEqual(
            list(arriendo.obligaciones.values_list('periodo', flat=True)),
            [
                date(2026, 10, 1),
                date(2026, 11, 1),
                date(2026, 12, 1),
            ],
        )

        arriendo.fecha_fin = date(2027, 2, 3)
        arriendo.save()
        self.assertEqual(arriendo.obligaciones.count(), 4)

    def test_ventas_crea_exactamente_el_numero_de_cuotas_indicado(self):
        venta = Venta.objects.create(
            inmueble=self.inmueble,
            comprador=self.persona,
            fecha_venta=date(2026, 10, 3),
            precio_venta=Decimal('10000000'),
        )
        financiamiento = Financiamiento.objects.create(
            venta=venta,
            pago_inicial=Decimal('2000000'),
            numero_cuotas=4,
            valor_cuota=Decimal('2000000'),
            fecha_inicio=date(2026, 10, 3),
        )

        self.assertEqual(financiamiento.cuotas.count(), 4)
