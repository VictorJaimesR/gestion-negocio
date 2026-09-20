from django.contrib import admin
from .models import Cuota, Persona, Inmueble, Venta, Financiamiento, Arriendo, ObligacionArriendo, Honorarios 

admin.site.register(Persona)
admin.site.register(Inmueble)
admin.site.register(Venta)
admin.site.register(Financiamiento)


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ['financiamiento', 'numero_cuota', 'fecha_vencimiento', 'valor_cuota', 'estado']

@admin.register(Arriendo)
class ArriendoAdmin(admin.ModelAdmin):
    list_display = ['inmueble', 'arrendatario', 'canon_mensual', 'dia_pago', 'estado']

@admin.register(ObligacionArriendo)
class ObligacionArriendoAdmin(admin.ModelAdmin):
    list_display = ['arriendo', 'periodo', 'fecha_vencimiento', 'valor_obligacion', 'estado']

@admin.register(Honorarios)
class HonorariosAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'concepto', 'valor_honorario', 'fecha_vencimiento', 'estado']
    