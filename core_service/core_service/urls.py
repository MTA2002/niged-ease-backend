from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Core Service API",
        default_version='v1',
        description="API documentation for Core Service",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('transactions/', include('transactions.urls')),
        path('financials/', include('financials.urls')),
        path('companies/', include('companies.urls')),
        path('inventory/', include('inventory.urls')),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API Endpoints
    path('transactions/', include('transactions.urls')),
    path('financials/', include('financials.urls')),
    path('companies/', include('companies.urls')),
    path('inventory/', include('inventory.urls')),
]