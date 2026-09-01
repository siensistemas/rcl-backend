from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Busca Me API",
        default_version='v1',
        description="""
        Plataforma SaaS Multi-Tenant para comercios locales.
        
        ## Caracteristicas
        - Multi-tenant (municipios)
        - Autenticacion JWT
        - Gestion de comercios
        - Promociones y cupones
        - Eventos y turismo
        - Bolsa de empleo
        - Clasificados
        - Sistema de calificaciones
        - Notificaciones push
        - Analitica en tiempo real
        """,
        contact=openapi.Contact(
            email="admin@siensistemas.com",
            url="https://www.siensistemas.com"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

api_v1_patterns = [
    # Auth & Users
    path('auth/', include('apps.users.urls')),
    
    # Tenants
    path('tenants/', include('apps.tenants.urls')),
    
    # Categories
    path('categories/', include('apps.categories.urls')),
    
    # Businesses
    path('businesses/', include('apps.businesses.urls')),
    
    # Promotions
    path('promotions/', include('apps.promotions.urls')),
    
    # Subscriptions
    path('subscriptions/', include('apps.subscriptions.urls')),

    # Merchant panel
    path('merchant/', include('apps.merchant.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
    
    # Swagger/OpenAPI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
