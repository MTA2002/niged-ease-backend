from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'inventory', InventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]