from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Arriendo, Financiamiento, Honorario, Inmueble, Movimiento, Persona, Venta


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

    def test_honorario_pagado_sin_movimientos_se_elimina(self):
        honorario = Honorario.objects.create(
            cliente=self.persona,
            concepto='Servicio de prueba',
            fecha_emision=date(2026, 10, 3),
            valor_honorario=Decimal('500000'),
            fecha_vencimiento=date(2026, 10, 3),
            estado=Honorario.ESTADO_PAGADA,
        )

        usuario = get_user_model().objects.create_user(
            username='usuario-prueba',
            password='clave-prueba',
        )
        cliente_api = APIClient()
        cliente_api.force_authenticate(user=usuario)
        respuesta = cliente_api.delete(f'/api/honorarios/{honorario.id}/')
        self.assertEqual(respuesta.status_code, 204)
        self.assertFalse(Honorario.objects.filter(pk=honorario.id).exists())
        self.assertFalse(Honorario.objects.filter(pk=honorario.id).exists())

    def test_honorario_pagado_con_movimiento_no_se_elimina(self):
        honorario = Honorario.objects.create(
            cliente=self.persona,
            concepto='Servicio protegido',
            fecha_emision=date(2026, 10, 3),
            valor_honorario=Decimal('500000'),
            fecha_vencimiento=date(2026, 10, 3),
        )
        movimiento = Movimiento.objects.create(
            tipo=Movimiento.TIPO_PAGO_HONORARIO,
            honorario=honorario,
            fecha=date(2026, 10, 3),
            valor=Decimal('500000'),
        )

        usuario = get_user_model().objects.create_user(
            username='usuario-protegido',
            password='clave-protegida',
        )
        cliente_api = APIClient()
        cliente_api.force_authenticate(user=usuario)
        respuesta = cliente_api.delete(f'/api/honorarios/{honorario.id}/')

        self.assertEqual(respuesta.status_code, 400)
        self.assertTrue(Honorario.objects.filter(pk=honorario.id).exists())
        self.assertTrue(Movimiento.objects.filter(pk=movimiento.id).exists())
