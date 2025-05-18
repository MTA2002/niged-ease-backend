from django.urls import path
from companies.views.company import (
    CompanyListView, 
    CompanyDetailView,
    CompanySubscriptionCheckView,
    CompanySubscriptionRenewView
)
from companies.views.store import (
    StoreListView,
    StoreDetailView
)
from companies.views.subscription_plan import SubscriptionPlanDetailView, SubscriptionPlanListView, SubscriptionPlanViewSet
from companies.views.currency import CurrencyListView, CurrencyDetailView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    # Company endpoints
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/<uuid:id>/', CompanyDetailView.as_view(), name='company-detail'),
    path('companies/<uuid:id>/subscription/check/', CompanySubscriptionCheckView.as_view(), name='company-subscription-check'),
    path('companies/<uuid:id>/subscription/renew/', CompanySubscriptionRenewView.as_view(), name='company-subscription-renew'),
    
    # Subscription plan endpoints
    path('subscription-plans/', SubscriptionPlanListView.as_view(), name='subscription-plan-list'),
    path('subscription-plans/<uuid:id>/', SubscriptionPlanDetailView.as_view(), name='subscription-plan-detail'),
    
    # Currency endpoints
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('currencies/<uuid:id>/', CurrencyDetailView.as_view(), name='currency-detail'),
    
    # Store URLs
    path('stores/', StoreListView.as_view(), name='store-list'),
    path('stores/<uuid:id>/', StoreDetailView.as_view(), name='store-detail'),
] 


