from django.urls import path
from .views import (
    RevenuePredictionAPIView,
    ProfitPredictionAPIView,
    CustomerPredictionAPIView,
    CompanyRevenuePredictionAPIView,
    CompanyProfitPredictionAPIView,
    CompanyCustomerPredictionAPIView
)

urlpatterns = [
    # Store-level predictions
    path(
        'stores/<uuid:store_id>/predictions/revenue/',
        RevenuePredictionAPIView.as_view(),
        name='predict_revenue'
    ),
    path(
        'stores/<uuid:store_id>/predictions/profit/',
        ProfitPredictionAPIView.as_view(),
        name='predict_profit'
    ),
    path(
        'stores/<uuid:store_id>/predictions/customers/',
        CustomerPredictionAPIView.as_view(),
        name='predict_customers'
    ),
    
    # Company-level predictions
    path(
        'companies/<uuid:company_id>/predictions/revenue/',
        CompanyRevenuePredictionAPIView.as_view(),
        name='predict_company_revenue'
    ),
    path(
        'companies/<uuid:company_id>/predictions/profit/',
        CompanyProfitPredictionAPIView.as_view(),
        name='predict_company_profit'
    ),
    path(
        'companies/<uuid:company_id>/predictions/customers/',
        CompanyCustomerPredictionAPIView.as_view(),
        name='predict_company_customers'
    ),
] 