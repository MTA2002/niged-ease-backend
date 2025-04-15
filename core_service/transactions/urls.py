from django.urls import path
from transactions.views.payment_mode import PaymentModeDetailView, PaymentModeListView
from transactions.views.customer import CustomerListView, CustomerDetailView
from transactions.views.supplier import SupplierListView, SupplierDetailView
from transactions.views.sale import (
    SaleListView, SaleDetailView,
    SaleItemListView, SaleItemDetailView
)
from transactions.views.purchase import (
    PurchaseListView, PurchaseDetailView,
    PurchaseItemListView, PurchaseItemDetailView
)

app_name = 'transactions'

urlpatterns = [
    # Customer URLs
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:id>/', CustomerDetailView.as_view(), name='customer-detail'),
    
    # Supplier URLs
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/<int:id>/', SupplierDetailView.as_view(), name='supplier-detail'),
    
    # Sale URLs
    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sales/<uuid:id>/', SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<uuid:sale_id>/items/', SaleItemListView.as_view(), name='sale-item-list'),
    path('sales/<uuid:sale_id>/items/<int:item_id>/', SaleItemDetailView.as_view(), name='sale-item-detail'),
    
    # Purchase URLs
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/<uuid:id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchases/<uuid:purchase_id>/items/', PurchaseItemListView.as_view(), name='purchase-item-list'),
    path('purchases/<uuid:purchase_id>/items/<int:item_id>/', PurchaseItemDetailView.as_view(), name='purchase-item-detail'),

     # Payment Mode URLs
    path('payment-modes/', PaymentModeListView.as_view(), name='payment-mode-list'),
    path('payment-modes/<uuid:id>/', PaymentModeDetailView.as_view(), name='payment-mode-detail'),
] 