from django.contrib import admin
from .models import Cuota, Persona, Inmueble, Venta, Financiamiento

admin.site.register(Persona)
admin.site.register(Inmueble)
admin.site.register(Venta)
admin.site.register(Financiamiento)

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ['financiamiento', 'numero_cuota', 'fecha_vencimiento', 'valor_cuota', 'estado']