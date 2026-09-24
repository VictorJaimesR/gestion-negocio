from django.urls import path
from rest_framework.routers import DefaultRouter
from .api_views import PersonaViewSet, InmuebleViewSet, VentaViewSet, FinanciamientoViewSet, CuotaViewSet, ArriendoViewSet, ObligacionArriendoViewSet, HonorarioViewSet, MovimientoViewSet, cuentas_por_cobrar

router = DefaultRouter()
router.register('personas', PersonaViewSet)
router.register('inmuebles', InmuebleViewSet)
router.register('ventas', VentaViewSet)
router.register('financiamientos', FinanciamientoViewSet)
router.register('cuotas', CuotaViewSet)
router.register('arriendos', ArriendoViewSet)
router.register('obligaciones-arriendo', ObligacionArriendoViewSet)
router.register('honorarios', HonorarioViewSet)
router.register('movimientos', MovimientoViewSet)

urlpatterns = router.urls + [
    path('cuentas-por-cobrar/', cuentas_por_cobrar),
]

