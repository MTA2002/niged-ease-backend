from django.urls import path
from inventory.views import (
    ProductListView,
    ProductDetailView,
    ProductCategoryListView,
    ProductCategoryDetailView,
    ProductUnitListView,
    ProductUnitDetailView
)
from inventory.views.inventory import InventoryListView, InventoryDetailView
from inventory.views.product_search import ProductSearchView

urlpatterns = [
    # Product URLs
    path('stores/<uuid:store_id>/products/', ProductListView.as_view(), name='product-list'),
    path('stores/<uuid:store_id>/products/<uuid:id>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Product Category URLs
    path('stores/<uuid:store_id>/product-categories/', ProductCategoryListView.as_view(), name='product-category-list'),
    path('stores/<uuid:store_id>/product-categories/<uuid:id>/', ProductCategoryDetailView.as_view(), name='product-category-detail'),
    
    # Product Unit URLs
    path('stores/<uuid:store_id>/product-units/', ProductUnitListView.as_view(), name='product-unit-list'),
    path('stores/<uuid:store_id>/product-units/<uuid:id>/', ProductUnitDetailView.as_view(), name='product-unit-detail'),
    
    # Inventory URLs
    path('stores/<uuid:store_id>/inventories/', InventoryListView.as_view(), name='inventory-list'),
    path('stores/<uuid:store_id>/inventories/<uuid:id>/', InventoryDetailView.as_view(), name='inventory-detail'),

    # Product Search URL
    path('companies/<uuid:company_id>/product-search/<str:search_term>/', ProductSearchView.as_view(), name='product-search-with-term'),
] 