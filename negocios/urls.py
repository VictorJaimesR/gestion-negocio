from django.urls import path
from . import views

urlpatterns = [
    path('cuentas_por_cobrar/', views.cuentas_por_cobrar, name= 'cuentas_por_cobrar'),]
