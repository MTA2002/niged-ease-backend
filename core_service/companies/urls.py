from django.urls import path
from companies.views.company import (
    CompanyListView, 
    CompanyDetailView,
    CompanySubscriptionCheckView,
    CompanySubscriptionRenewView
)
from companies.views.subscription_plan import SubscriptionPlanViewSet
from companies.views.currency import CurrencyListView, CurrencyDetailView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')

urlpatterns = [
    # Company endpoints
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/<uuid:id>/', CompanyDetailView.as_view(), name='company-detail'),
    path('companies/<uuid:id>/subscription/check/', CompanySubscriptionCheckView.as_view(), name='company-subscription-check'),
    path('companies/<uuid:id>/subscription/renew/', CompanySubscriptionRenewView.as_view(), name='company-subscription-renew'),
    
    # Currency endpoints
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('currencies/<uuid:id>/', CurrencyDetailView.as_view(), name='currency-detail'),
]

urlpatterns += router.urls 