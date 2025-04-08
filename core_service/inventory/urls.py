from django.urls import path
from inventory.views import (
    ProductListView,
    ProductDetailView,
    ProductCategoryListView,
    ProductCategoryDetailView,
    ProductUnitListView,
    ProductUnitDetailView,
    StoreListView,
    StoreDetailView
)

urlpatterns = [
    # Product URLs
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<uuid:id>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Product Category URLs
    path('product-categories/', ProductCategoryListView.as_view(), name='product-category-list'),
    path('product-categories/<uuid:id>/', ProductCategoryDetailView.as_view(), name='product-category-detail'),
    
    # Product Unit URLs
    path('product-units/', ProductUnitListView.as_view(), name='product-unit-list'),
    path('product-units/<uuid:id>/', ProductUnitDetailView.as_view(), name='product-unit-detail'),
    
    # Store URLs
    path('stores/', StoreListView.as_view(), name='store-list'),
    path('stores/<uuid:id>/', StoreDetailView.as_view(), name='store-detail'),
] 