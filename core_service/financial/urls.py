from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentModeViewSet, CurrencyViewSet, SubscriptionPlanViewSet, CompanyViewSet,
    SaleViewSet, SaleItemViewSet, PurchaseViewSet, PurchaseItemViewSet,
    ExpenseCategoryViewSet, ExpenseViewSet, PayableViewSet, ReceivableViewSet,
    BankViewSet, PaymentOutViewSet, PaymentInViewSet, ReportViewSet, SignupView
)

router = DefaultRouter()
router.register(r'payment-modes', PaymentModeViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'sale-items', SaleItemViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'purchase-items', PurchaseItemViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'payables', PayableViewSet)
router.register(r'receivables', ReceivableViewSet)
router.register(r'banks', BankViewSet)
router.register(r'payment-outs', PaymentOutViewSet)
router.register(r'payment-ins', PaymentInViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
]