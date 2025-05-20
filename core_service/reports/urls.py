from django.urls import path
from reports.views import (
    ReportListView,
    GenerateSalesReportView,
    GenerateInventoryReportView,
    GenerateFinancialReportView,
    GenerateCustomerReportView,
    GenerateProductPerformanceReportView,
    GenerateProfitReportView,
    GenerateRevenueReportView
)

urlpatterns = [
    # List all reports for a store
    path('stores/<uuid:store_id>/reports/', ReportListView.as_view(), name='report-list'),
    
    # Generate different types of reports
    path('stores/<uuid:store_id>/reports/sales/', GenerateSalesReportView.as_view(), name='generate-sales-report'),
    path('stores/<uuid:store_id>/reports/inventory/', GenerateInventoryReportView.as_view(), name='generate-inventory-report'),
    path('stores/<uuid:store_id>/reports/financials/', GenerateFinancialReportView.as_view(), name='generate-financial-report'),
    path('stores/<uuid:store_id>/reports/customers/', GenerateCustomerReportView.as_view(), name='generate-customer-report'),
    path('stores/<uuid:store_id>/reports/products/', GenerateProductPerformanceReportView.as_view(), name='generate-product-report'),
    path('stores/<uuid:store_id>/reports/profit/', GenerateProfitReportView.as_view(), name='generate-profit-report'),
    path('stores/<uuid:store_id>/reports/revenue/', GenerateRevenueReportView.as_view(), name='generate-revenue-report'),
] 