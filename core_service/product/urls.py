from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductUnitViewSet, ProductCategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'units', ProductUnitViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]