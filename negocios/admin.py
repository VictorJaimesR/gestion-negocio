from django.contrib import admin
from .models import Cuota, Persona, Inmueble, Venta, Financiamiento, Arriendo, ObligacionArriendo, Honorario, Movimiento

admin.site.register(Persona)
admin.site.register(Inmueble)



class CuotaInline(admin.TabularInline):
    model = Cuota
    extra = 0

@admin.register(Financiamiento)
class FinanciamientoAdmin(admin.ModelAdmin):
    list_display = ['venta', 'pago_inicial', 'numero_cuotas', 'valor_cuota', 'fecha_inicio']
    inlines = [CuotaInline]



class FinanciamientoInline(admin.StackedInline):
    model = Financiamiento
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['inmueble', 'comprador', 'precio_venta', 'fecha_venta']
    inlines = [FinanciamientoInline]

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ['financiamiento', 'numero_cuota', 'fecha_vencimiento', 'valor_cuota', 'estado']


class ObligacionArriendoInline(admin.TabularInline):
    model = ObligacionArriendo
    extra = 0
    
@admin.register(Arriendo)
class ArriendoAdmin(admin.ModelAdmin):
    list_display = ['inmueble', 'arrendatario', 'canon_mensual', 'dia_pago', 'estado']
    inlines = [ObligacionArriendoInline]

@admin.register(ObligacionArriendo)
class ObligacionArriendoAdmin(admin.ModelAdmin):
    list_display = ['arriendo', 'periodo', 'fecha_vencimiento', 'valor_obligacion', 'estado']

@admin.register(Honorario)
class HonorarioAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'concepto', 'valor_honorario', 'fecha_vencimiento', 'estado']

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'valor', 'fecha']
