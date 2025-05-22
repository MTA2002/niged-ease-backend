# from django.db import models
# import uuid
# from django.utils import timezone
# from decimal import Decimal

# class Report(models.Model):
#     class ReportType(models.TextChoices):
#         SALES = 'SALES', 'Sales Report'
#         INVENTORY = 'INVENTORY', 'Inventory Report'
#         FINANCIAL = 'FINANCIAL', 'Financial Report'
#         CUSTOMER = 'CUSTOMER', 'Customer Report'
#         PRODUCT = 'PRODUCT', 'Product Performance Report'
#         PROFIT = 'PROFIT', 'Profit Report'
#         REVENUE = 'REVENUE', 'Revenue Report'
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     store = models.ForeignKey('companies.Store', on_delete=models.CASCADE)
#     report_type = models.CharField(max_length=20, choices=ReportType.choices)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     date_range_start = models.DateTimeField()
#     date_range_end = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"{self.title} - {self.store.name}"


# class SalesReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     total_sales = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_items_sold = models.IntegerField(default=0)
#     average_sale_value = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0')) 
#     highest_sale_value = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_credit_sales = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_cash_sales = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     top_selling_products = models.JSONField(default=dict)
#     daily_sales_breakdown = models.JSONField(default=dict)
    
#     def __str__(self):
#         return f"Sales Report - {self.report.store.name}"


# class InventoryReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     total_products = models.IntegerField(default=0)
#     low_stock_products = models.JSONField(default=dict)
#     out_of_stock_products = models.JSONField(default=dict)
#     overstocked_products = models.JSONField(default=dict)
#     inventory_value = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     inventory_turnover_rate = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
#     def __str__(self):
#         return f"Inventory Report - {self.report.store.name}"


# class FinancialReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     total_sales = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_expenses = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_purchases = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_payment_ins = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     total_payment_outs = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     gross_profit = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     net_profit = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     profit_margin_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
#     expense_breakdown = models.JSONField(default=dict)
    
#     def __str__(self):
#         return f"Financial Report - {self.report.store.name}"


# class CustomerReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     total_customers = models.IntegerField(default=0)
#     new_customers = models.IntegerField(default=0)
#     returning_customers = models.IntegerField(default=0)
#     top_customers = models.JSONField(default=dict)
#     average_purchase_value = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     customer_retention_rate = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
#     def __str__(self):
#         return f"Customer Report - {self.report.store.name}"


# class ProductPerformanceReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     top_performing_products = models.JSONField(default=dict)
#     worst_performing_products = models.JSONField(default=dict)
#     product_category_breakdown = models.JSONField(default=dict)
#     seasonal_product_trends = models.JSONField(default=dict)
    
#     def __str__(self):
#         return f"Product Performance Report - {self.report.store.name}"


# class ProfitReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     gross_profit = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     net_profit = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     profit_margin_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
#     sales_revenue = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     cost_of_goods_sold = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     operating_expenses = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     profit_by_product_category = models.JSONField(default=dict)
#     profit_trend = models.JSONField(default=dict)  # Daily/monthly trend data
    
#     def __str__(self):
#         return f"Profit Report - {self.report.store.name}"


# class RevenueReport(models.Model):
#     report = models.OneToOneField(Report, on_delete=models.CASCADE, primary_key=True)
#     total_revenue = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     sales_revenue = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     other_revenue = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
#     revenue_by_payment_mode = models.JSONField(default=dict)
#     revenue_by_product_category = models.JSONField(default=dict)
#     daily_revenue = models.JSONField(default=dict)
#     monthly_revenue = models.JSONField(default=dict)
#     average_daily_revenue = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
    
#     def __str__(self):
#         return f"Revenue Report - {self.report.store.name}"
