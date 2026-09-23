from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('negocios/', include('negocios.urls')),
    path('api/', include('negocios.api_urls')),

]
