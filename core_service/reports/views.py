from django.shortcuts import render
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, F, Q, Max
from django.db import models
from django.utils import timezone
from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from transactions.models.sale import Sale
from transactions.models.sale_item import SaleItem
from transactions.models.purchase import Purchase
from transactions.models.purchase_item import PurchaseItem
from companies.models.store import Store
from inventory.models.product import Product
from inventory.models.inventory import Inventory
from financials.models.expense import Expense
from financials.models.payment_in import PaymentIn
from financials.models.payment_out import PaymentOut
from reports.models import (
    Report, 
    SalesReport, 
    InventoryReport, 
    FinancialReport, 
    CustomerReport, 
    ProductPerformanceReport,
    ProfitReport,
    RevenueReport
)
from reports.serializers import (
    ReportSerializer,
    SalesReportSerializer,
    InventoryReportSerializer,
    FinancialReportSerializer,
    CustomerReportSerializer,
    ProductPerformanceReportSerializer,
    ProfitReportSerializer,
    RevenueReportSerializer
)


class ReportListView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Get available report types for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH)
        ],
        responses={200: {"type": "object"}}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        available_reports = [
            {
                "type": "sales",
                "name": "Sales Report",
                "description": "Shows sales performance, top-selling products, and sales trends",
                "endpoint": f"/reports/stores/{store_id}/reports/sales/",
                "supports_date_range": True
            },
            {
                "type": "inventory",
                "name": "Inventory Report",
                "description": "Shows current inventory status, low stock items, and inventory value",
                "endpoint": f"/reports/stores/{store_id}/reports/inventory/",
                "supports_date_range": False
            },
            {
                "type": "financial",
                "name": "Financial Report",
                "description": "Shows financial performance including expenses, purchases, and profit metrics",
                "endpoint": f"/reports/stores/{store_id}/reports/financials/",
                "supports_date_range": True
            },
            {
                "type": "customer",
                "name": "Customer Report",
                "description": "Shows customer metrics, new vs returning customers, and top customers",
                "endpoint": f"/reports/stores/{store_id}/reports/customers/",
                "supports_date_range": True
            },
            {
                "type": "product",
                "name": "Product Performance Report",
                "description": "Shows product performance metrics, category breakdown, and seasonal trends",
                "endpoint": f"/reports/stores/{store_id}/reports/products/",
                "supports_date_range": True
            },
            {
                "type": "profit",
                "name": "Profit Report",
                "description": "Shows detailed profit analysis, margins, and profit trends",
                "endpoint": f"/reports/stores/{store_id}/reports/profit/",
                "supports_date_range": True
            },
            {
                "type": "revenue",
                "name": "Revenue Report",
                "description": "Shows revenue streams, payment modes, and revenue trends",
                "endpoint": f"/reports/stores/{store_id}/reports/revenue/",
                "supports_date_range": True
            }
        ]
        
        return Response({"store": str(store_id), "store_name": store.name, "available_reports": available_reports}, status=status.HTTP_200_OK)


class GenerateSalesReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a sales report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: SalesReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales data
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate sales metrics
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get credit sales
        credit_sales = sales.filter(is_credit=True).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get cash sales
        cash_sales = sales.filter(is_credit=False).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get highest sale
        highest_sale = sales.aggregate(max_sale=Max('total_amount'))['max_sale'] or Decimal('0')
        
        # Get sale items
        sale_items = SaleItem.objects.filter(sale__in=sales)
        total_items = sale_items.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate average sale value
        avg_sale = Decimal('0')
        if sales.count() > 0:
            avg_sale = total_sales / sales.count()
            
        # Get top selling products
        top_products = sale_items.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('product__price'))
        ).order_by('-total_quantity')[:10]
        
        top_products_data = []
        for item in top_products:
            try:
                product = Product.objects.get(pk=item['product'])
                top_products_data.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'total_quantity': float(item['total_quantity']),
                    'total_sales': float(item.get('total_sales', 0))
                })
            except Product.DoesNotExist:
                continue
        
        # Calculate daily sales breakdown
        daily_sales = {}
        for sale in sales:
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in daily_sales:
                daily_sales[day] = {
                    'date': day,
                    'total': 0,
                    'count': 0
                }
            daily_sales[day]['total'] += float(sale.total_amount)
            daily_sales[day]['count'] += 1
        
        daily_sales_list = list(daily_sales.values())
        
        # Prepare report response data
        report_data = {
            "title": f"Sales Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Sales performance from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_sales": float(total_sales),
            "total_items_sold": total_items if total_items else 0,
            "average_sale_value": float(avg_sale),
            "highest_sale_value": float(highest_sale),
            "total_credit_sales": float(credit_sales),
            "total_cash_sales": float(cash_sales),
            "top_selling_products": top_products_data,
            "daily_sales_breakdown": daily_sales_list
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateInventoryReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate an inventory report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH)
        ],
        responses={200: InventoryReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get inventory data
        inventory_items = Inventory.objects.filter(store=store)
        total_products = inventory_items.count()
        
        # Calculate inventory value
        inventory_value = Decimal('0')
        for item in inventory_items:
            try:
                # Based on the actual Product model, it uses sale_price field
                item_value = item.quantity * item.product.sale_price
                inventory_value += item_value
            except:
                pass
        
        # Identify low stock items (less than 10 units as default threshold)
        low_stock_threshold = 10  # Default threshold
        low_stock_items = []
        for item in inventory_items:
            if item.quantity < low_stock_threshold:
                low_stock_items.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'current_quantity': float(item.quantity),
                    'threshold': low_stock_threshold
                })
        
        # Identify out of stock items
        out_of_stock_items = []
        for item in inventory_items:
            if item.quantity <= 0:
                out_of_stock_items.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'last_stocked': item.updated_at.strftime('%Y-%m-%d') if item.updated_at else None
                })
        
        # Identify overstocked items (more than 100 units as default)
        high_stock_threshold = 100  # Default threshold
        overstocked_items = []
        for item in inventory_items:
            if item.quantity > high_stock_threshold:
                overstocked_items.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'current_quantity': float(item.quantity),
                    'threshold': high_stock_threshold
                })
        
        # Calculate inventory turnover rate (if sales data is available)
        inventory_turnover = Decimal('0')
        try:
            # Get sales from the past 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            # Calculate COGS (cost of goods sold) from sold items
            sold_items = SaleItem.objects.filter(
                sale__store_id=store,
                sale__created_at__gte=thirty_days_ago
            )
            
            cogs = Decimal('0')
            for item in sold_items:
                try:
                    # Based on the actual Product model, it uses purchase_price field for cost
                    cost = item.product.purchase_price
                    cogs += cost * item.quantity
                except:
                    pass
            
            if inventory_value > 0:
                inventory_turnover = cogs / inventory_value
            
        except Exception as e:
            print(f"Error calculating inventory turnover: {e}")
            inventory_turnover = Decimal('0')
        
        
        # Prepare report data
        report_data = {
            "title": f"Inventory Report {timezone.now().strftime('%Y-%m-%d')}",
            "description": f"Current inventory status as of {timezone.now().strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": timezone.now(),
            "date_range_end": timezone.now(),
            "total_products": total_products,
            "low_stock_products": low_stock_items,
            "out_of_stock_products": out_of_stock_items,
            "overstocked_products": overstocked_items,
            "inventory_value": float(inventory_value),
            "inventory_turnover_rate": float(inventory_turnover)
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateFinancialReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a financial report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: FinancialReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales data
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get real data for financials
        # Get expenses
        expenses = Expense.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get purchases
        purchases = Purchase.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_purchases = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get payment ins
        payment_ins = PaymentIn.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_payment_ins = payment_ins.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get payment outs
        payment_outs = PaymentOut.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_payment_outs = payment_outs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate profits
        gross_profit = total_sales - total_purchases
        net_profit = gross_profit - total_expenses
        
        # Calculate profit margin
        profit_margin = Decimal('0')
        if total_sales > 0:
            profit_margin = (net_profit / total_sales) * 100
        
        # Get expense breakdown by category
        expense_breakdown = {}
        for expense in expenses:
            try:
                category_name = expense.expense_category.name
                if category_name not in expense_breakdown:
                    expense_breakdown[category_name] = 0
                expense_breakdown[category_name] += float(expense.amount)
            except:
                if 'Other' not in expense_breakdown:
                    expense_breakdown['Other'] = 0
                expense_breakdown['Other'] += float(expense.amount)
        
        # Prepare report data
        report_data = {
            "title": f"Financial Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Financial performance from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_sales": float(total_sales),
            "total_expenses": float(total_expenses),
            "total_purchases": float(total_purchases),
            "total_payment_ins": float(total_payment_ins),
            "total_payment_outs": float(total_payment_outs),
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "profit_margin_percentage": float(profit_margin),
            "expense_breakdown": expense_breakdown
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateCustomerReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a customer report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: CustomerReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales for the period
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Get unique customers from the sales
        customers = sales.values('customer').distinct()
        total_customers = customers.count()
        
        # Previous period for comparison (same length)
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        # Get customers who made purchases in previous period
        prev_customers = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=prev_start,
            created_at__lte=prev_end
        ).values('customer').distinct()
        
        # New customers are those who didn't make purchases in the previous period
        prev_customer_ids = set(item['customer'] for item in prev_customers)
        new_customer_count = 0
        for customer in customers:
            if customer['customer'] not in prev_customer_ids:
                new_customer_count += 1
        
        # Returning customers are those who did make purchases in both periods
        returning_customer_count = total_customers - new_customer_count
        
        # Calculate average purchase value
        avg_purchase = Decimal('0')
        if sales.count() > 0:
            total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            avg_purchase = total_sales / sales.count()
        
        # Get top customers
        top_customers_data = []
        top_customers = sales.values('customer').annotate(
            total_spent=Sum('total_amount'), 
            purchase_count=Count('id')
        ).order_by('-total_spent')[:10]
        
        for item in top_customers:
            top_customers_data.append({
                'customer_id': str(item['customer']),
                'total_spent': float(item['total_spent']),
                'purchase_count': item['purchase_count'],
            })
        
        # Calculate retention rate
        retention_rate = Decimal('0')
        if total_customers > 0:
            retention_rate = (Decimal(returning_customer_count) / Decimal(total_customers)) * 100
        
        print(total_customers)
        # Prepare report data
        report_data = {
            "title": f"Customer Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Customer analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_customers": total_customers,
            "new_customers": new_customer_count,
            "returning_customers": returning_customer_count,
            "top_customers": top_customers_data,
            "average_purchase_value": float(avg_purchase),
            "customer_retention_rate": float(retention_rate)
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateProductPerformanceReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a product performance report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: ProductPerformanceReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales for the period
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Get sale items
        sale_items = SaleItem.objects.filter(sale__in=sales)
        
        # Analyze product performance - top sellers
        top_products = sale_items.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('product__price'))
        ).order_by('-total_revenue')[:10]
        
        top_products_data = []
        for item in top_products:
            try:
                product = Product.objects.get(pk=item['product'])
                top_products_data.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'total_quantity': float(item['total_quantity']),
                    'total_revenue': float(item.get('total_revenue', 0)),
                    'profit_margin': float(item.get('total_revenue', 0)) - (float(item['total_quantity']) * float(product.purchase_price if hasattr(product, 'cost_price') else 0))
                })
            except Product.DoesNotExist:
                continue
        
        # Worst performing products (lowest revenue)
        worst_products = sale_items.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('product__price'))
        ).order_by('total_revenue')[:10]
        
        worst_products_data = []
        for item in worst_products:
            try:
                product = Product.objects.get(pk=item['product'])
                worst_products_data.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'total_quantity': float(item['total_quantity']),
                    'total_revenue': float(item.get('total_revenue', 0))
                })
            except Product.DoesNotExist:
                continue
        
        # Analyze by category
        category_breakdown = {}
        for item in sale_items:
            try:
                category = item.product.product_category.name if hasattr(item.product, 'product_category') else "Uncategorized"
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'total_quantity': 0,
                        'total_revenue': 0
                    }
                
                category_breakdown[category]['total_quantity'] += float(item.quantity)
                category_breakdown[category]['total_revenue'] += float(item.quantity * item.product.sale_price)
            except:
                pass
        
        # Convert to list for JSON storage
        category_data = [{"category": k, **v} for k, v in category_breakdown.items()]
        
        # Analyze seasonal trends (by month)
        seasonal_trends = {}
        for sale in sales:
            month = sale.created_at.strftime('%Y-%m')
            if month not in seasonal_trends:
                seasonal_trends[month] = {
                    'month': month,
                    'total_sales': 0,
                    'product_breakdown': {}
                }
            
            seasonal_trends[month]['total_sales'] += float(sale.total_amount)
            
            # Add product breakdown for this month
            sale_items_for_sale = SaleItem.objects.filter(sale=sale)
            for item in sale_items_for_sale:
                try:
                    product_name = item.product.name
                    if product_name not in seasonal_trends[month]['product_breakdown']:
                        seasonal_trends[month]['product_breakdown'][product_name] = 0
                    
                    seasonal_trends[month]['product_breakdown'][product_name] += float(item.quantity)
                except:
                    pass
        
        # Convert to list for JSON storage
        seasonal_data = list(seasonal_trends.values())
        
        # Prepare report data
        report_data = {
            "title": f"Product Performance Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Product performance analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "top_performing_products": top_products_data,
            "worst_performing_products": worst_products_data,
            "product_category_breakdown": category_data,
            "seasonal_product_trends": seasonal_data
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateProfitReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a profit report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: ProfitReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales data for the period
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate sales revenue
        sales_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Calculate cost of goods sold (COGS)
        sale_items = SaleItem.objects.filter(sale__in=sales)
        cost_of_goods_sold = Decimal('0')
        
        for item in sale_items:
            try:
                # Use product's purchase price as the cost
                cost_of_goods_sold += item.quantity * item.product.purchase_price
            except:
                pass
        
        # Get expenses for the period
        expenses = Expense.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        operating_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate gross and net profit
        gross_profit = sales_revenue - cost_of_goods_sold
        net_profit = gross_profit - operating_expenses
        
        # Calculate profit margin
        profit_margin = Decimal('0')
        if sales_revenue > 0:
            profit_margin = (net_profit / sales_revenue) * 100
        
        # Calculate profit by product category
        profit_by_category = {}
        
        for item in sale_items:
            try:
                category_name = item.product.product_category.name
                if category_name not in profit_by_category:
                    profit_by_category[category_name] = {
                        'revenue': 0,
                        'cost': 0,
                        'profit': 0
                    }
                
                # Calculate revenue and cost for this item
                item_revenue = float(item.quantity * item.product.sale_price)
                item_cost = float(item.quantity * item.product.purchase_price)
                
                profit_by_category[category_name]['revenue'] += item_revenue
                profit_by_category[category_name]['cost'] += item_cost
                profit_by_category[category_name]['profit'] += (item_revenue - item_cost)
            except:
                pass
        
        # Convert to list for JSON storage
        profit_by_category_list = [{"category": k, **v} for k, v in profit_by_category.items()]
        
        # Calculate profit trend by day
        profit_trend = {}
        for sale in sales:
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in profit_trend:
                profit_trend[day] = {
                    'date': day,
                    'revenue': 0,
                    'cost': 0,
                    'profit': 0
                }
            
            # Add sale revenue
            profit_trend[day]['revenue'] += float(sale.total_amount)
            
            # Calculate cost for this sale
            sale_items_for_sale = SaleItem.objects.filter(sale=sale)
            sale_cost = 0
            for item in sale_items_for_sale:
                try:
                    sale_cost += float(item.quantity * item.product.purchase_price)
                except:
                    pass
            
            profit_trend[day]['cost'] += sale_cost
            profit_trend[day]['profit'] = profit_trend[day]['revenue'] - profit_trend[day]['cost']
        
        # Convert to list for JSON storage
        profit_trend_list = list(profit_trend.values())
        
        # Prepare report data
        report_data = {
            "title": f"Profit Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Profit analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "profit_margin_percentage": float(profit_margin),
            "sales_revenue": float(sales_revenue),
            "cost_of_goods_sold": float(cost_of_goods_sold),
            "operating_expenses": float(operating_expenses),
            "profit_by_product_category": profit_by_category_list,
            "profit_trend": profit_trend_list
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateRevenueReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a revenue report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ],
        responses={200: RevenueReportSerializer}
    )
    def get(self, request: Request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)  # End of day
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sales data for the period
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate sales revenue
        sales_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get other revenue (e.g. payment_ins that are not associated with sales)
        other_revenue_sources = PaymentIn.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date,
            sale__isnull=True  # Only include payments not tied to sales
        )
        
        other_revenue = other_revenue_sources.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate total revenue
        total_revenue = sales_revenue + other_revenue
        
        # Calculate revenue by payment mode
        revenue_by_payment = {}
        
        for sale in sales:
            payment_mode_name = sale.payment_mode.name if sale.payment_mode else "Unspecified"
            if payment_mode_name not in revenue_by_payment:
                revenue_by_payment[payment_mode_name] = 0
            
            revenue_by_payment[payment_mode_name] += float(sale.total_amount)
        
        # Get revenue by product category
        revenue_by_category = {}
        
        sale_items = SaleItem.objects.filter(sale__in=sales)
        for item in sale_items:
            try:
                category_name = item.product.product_category.name
                if category_name not in revenue_by_category:
                    revenue_by_category[category_name] = 0
                
                item_revenue = float(item.quantity * item.product.sale_price)
                revenue_by_category[category_name] += item_revenue
            except:
                pass
        
        # Convert to list for JSON storage
        revenue_by_category_list = [{"category": k, "amount": v} for k, v in revenue_by_category.items()]
        revenue_by_payment_list = [{"payment_mode": k, "amount": v} for k, v in revenue_by_payment.items()]
        
        # Calculate daily revenue
        daily_revenue = {}
        for sale in sales:
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in daily_revenue:
                daily_revenue[day] = {
                    'date': day,
                    'amount': 0,
                    'transaction_count': 0
                }
            
            daily_revenue[day]['amount'] += float(sale.total_amount)
            daily_revenue[day]['transaction_count'] += 1
        
        # Convert to list for JSON storage
        daily_revenue_list = list(daily_revenue.values())
        
        # Calculate monthly revenue
        monthly_revenue = {}
        for sale in sales:
            month = sale.created_at.strftime('%Y-%m')
            if month not in monthly_revenue:
                monthly_revenue[month] = {
                    'month': month,
                    'amount': 0,
                    'transaction_count': 0
                }
            
            monthly_revenue[month]['amount'] += float(sale.total_amount)
            monthly_revenue[month]['transaction_count'] += 1
        
        # Convert to list for JSON storage
        monthly_revenue_list = list(monthly_revenue.values())
        
        # Calculate average daily revenue
        days_in_period = (end_date - start_date).days + 1
        average_daily_revenue = total_revenue / days_in_period if days_in_period > 0 else Decimal('0')
        
        # Prepare report data
        report_data = {
            "title": f"Revenue Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Revenue analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_revenue": float(total_revenue),
            "sales_revenue": float(sales_revenue),
            "other_revenue": float(other_revenue),
            "revenue_by_payment_mode": revenue_by_payment_list,
            "revenue_by_product_category": revenue_by_category_list,
            "daily_revenue": daily_revenue_list,
            "monthly_revenue": monthly_revenue_list,
            "average_daily_revenue": float(average_daily_revenue)
        }
        
        return Response(report_data, status=status.HTTP_200_OK)
    