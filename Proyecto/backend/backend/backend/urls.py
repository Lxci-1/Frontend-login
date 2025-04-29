from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Login API",
        default_version='v1',
        description="Documentación de la API de Login",
        terms_of_service="https://www.miempresa.com/terms/",
        contact=openapi.Contact(email="soporte@miempresa.com"),
        license=openapi.License(name="Licencia BSD"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Permite el acceso público
)

urlpatterns = [
    # Ruta para el panel de administración de Django
    path('admin/', admin.site.urls),

    # Rutas para la API de login (esta ruta debe estar incluida en el 'login_app.urls')
    path('api/', include('login_app.urls')),

    # Ruta para acceder a Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Ruta para acceder a Redoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Ruta para obtener la documentación en formato JSON o YAML
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
