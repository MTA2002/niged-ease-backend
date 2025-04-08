from django.urls import path
from companies.views.company import (
    CompanyListView,
    CompanyDetailView
)
from companies.views.subscription_plan import (
    SubscriptionPlanListView,
    SubscriptionPlanDetailView
)
from companies.views.currency import (
    CurrencyListView,
    CurrencyDetailView
)

urlpatterns = [
    # Company URLs
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/<uuid:id>/', CompanyDetailView.as_view(), name='company-detail'),
    
    # Subscription Plan URLs
    path('subscription-plans/', SubscriptionPlanListView.as_view(), name='subscription-plan-list'),
    path('subscription-plans/<uuid:id>/', SubscriptionPlanDetailView.as_view(), name='subscription-plan-detail'),
    
    # Currency URLs
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('currencies/<uuid:id>/', CurrencyDetailView.as_view(), name='currency-detail'),
] 