from django.shortcuts import render
from django.db.models import Sum
from .models import Cuota, ObligacionArriendo, Honorario


def cuentas_por_cobrar(request):
    total_ventas = Cuota.objects.filter(estado__in=['pendiente', 'parcialmente_pagada']).aggregate(total=Sum('valor_cuota'))['total'] or 0

    total_arriendos = ObligacionArriendo.objects.filter(estado__in=['pendiente', 'parcialmente_pagada']).aggregate(total=Sum('valor_obligacion'))['total'] or 0

    total_honorarios = Honorario.objects.filter(estado__in=['pendiente', 'parcialmente_pagada']).aggregate(total=Sum('valor_honorario'))['total'] or 0

    total_general= total_ventas + total_arriendos + total_honorarios

    contexto = {
        'total_ventas': total_ventas,
        'total_arriendos': total_arriendos,
        'total_honorarios': total_honorarios,
        'total_general': total_general,
    }

    return render(request, 'negocios/cuentas_por_cobrar.html', contexto)