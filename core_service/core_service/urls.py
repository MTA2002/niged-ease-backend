from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    
    path('api-docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # API Endpoints
    path('transactions/', include('transactions.urls')),
    path('financials/', include('financials.urls')),
    path('companies/', include('companies.urls')),
    path('inventory/', include('inventory.urls')),
    path('clothings/', include('clothings.urls')),
    path('reports/', include('reports.urls')),
    path('api/predictions/', include('predictions.urls')),
]