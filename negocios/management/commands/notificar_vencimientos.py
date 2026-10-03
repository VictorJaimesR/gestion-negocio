from datetime import timedelta

from django.core.management.base import BaseCommand
from negocios.emails import enviar_correo
from django.utils import timezone

from negocios.models import Cuota, Honorario, ObligacionArriendo


class Command(BaseCommand):
    help = 'Envía recordatorios por email sobre pagos próximos a vencer.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Cantidad de días de anticipación para enviar el recordatorio.',
        )

    def handle(self, *args, **options):
        dias = options['dias']
        if dias < 0:
            self.stdout.write(self.style.ERROR('--dias no puede ser negativo.'))
            return

        hoy = timezone.localdate()
        fecha_limite = hoy + timedelta(days=dias)
        enviados = 0
        omitidos = 0
        errores = 0

        notificaciones = [
            (
                Cuota.objects.select_related(
                    'financiamiento__venta__comprador',
                ).filter(
                    estado__in=['pendiente', 'parcialmente_pagada'],
                    notificado=False,
                    fecha_vencimiento__range=(hoy, fecha_limite),
                ),
                'cuota de venta',
                'valor_cuota',
                lambda registro: registro.financiamiento.venta.comprador,
            ),
            (
                ObligacionArriendo.objects.select_related(
                    'arriendo__arrendatario',
                ).filter(
                    estado__in=['pendiente', 'parcialmente_pagada'],
                    notificado=False,
                    fecha_vencimiento__range=(hoy, fecha_limite),
                ),
                'obligación de arriendo',
                'valor_obligacion',
                lambda registro: registro.arriendo.arrendatario,
            ),
            (
                Honorario.objects.select_related('cliente').filter(
                    estado__in=['pendiente', 'parcialmente_pagada'],
                    notificado=False,
                    fecha_vencimiento__range=(hoy, fecha_limite),
                ),
                'honorario',
                'valor_honorario',
                lambda registro: registro.cliente,
            ),
        ]

        for registros, tipo_pago, campo_valor, obtener_cliente in notificaciones:
            for registro in registros:
                cliente = obtener_cliente(registro)
                email = cliente.email.strip()
                if not email:
                    omitidos += 1
                    self.stdout.write(
                        f'Se omitió {tipo_pago} de {cliente.nombre}: no tiene email.'
                    )
                    continue

                asunto = 'Recordatorio de pago próximo a vencer'
                cuerpo = (
                    f'Hola {cliente.nombre},\n\n'
                    f'Tienes un pago de tipo {tipo_pago} por valor de '
                    f'{getattr(registro, campo_valor)}, '
                    f'con fecha de vencimiento {registro.fecha_vencimiento:%d/%m/%Y}.\n\n'
                    'Por favor, realiza el pago antes de la fecha indicada.'
                )

                try:
                    enviar_correo(email, asunto, cuerpo)
                except Exception as error:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error enviando {tipo_pago} a {email}: {error}'
                        )
                    )
                    continue

                registro.notificado = True
                registro.save(update_fields=['notificado'])
                enviados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Resumen: {enviados} correos enviados, '
                f'{omitidos} omitidos por falta de email, '
                f'{errores} errores de envío.'
            )
        )
