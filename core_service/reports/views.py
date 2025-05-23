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
from transactions.models.customer import Customer
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
from transactions.models.supplier import Supplier
# from reports.models import (
#     Report, 
#     SalesReport, 
#     InventoryReport, 
#     FinancialReport, 
#     CustomerReport, 
#     ProductPerformanceReport,
#     ProfitReport,
#     RevenueReport
# )
# from reports.serializers import (
#     ReportSerializer,
#     SalesReportSerializer,
#     InventoryReportSerializer,
#     FinancialReportSerializer,
#     CustomerReportSerializer,
#     ProductPerformanceReportSerializer,
#     ProfitReportSerializer,
#     RevenueReportSerializer
# )


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
            },
            {
                "type": "purchase",
                "name": "Purchase Report",
                "description": "Shows purchase performance, supplier analysis, and payment efficiency",
                "endpoint": f"/reports/stores/{store_id}/reports/purchases/",
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
        ]
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
        
        # Calculate comprehensive sales metrics
        total_sales_amount_received = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Calculate actual expected amounts and payment status
        cash_sales = Decimal('0')  # Fully paid sales
        credit_sales = Decimal('0')  # Outstanding amount from unpaid/partially paid sales
        total_expected_amount = Decimal('0')  # Total amount that should have been received
        partially_paid_amount = Decimal('0')  # Amount received for partially paid sales
        unpaid_count = 0
        partially_paid_count = 0
        fully_paid_count = 0
        
        for sale in sales:
            # Calculate the actual expected amount for this sale (including tax)
            sale_items = SaleItem.objects.filter(sale=sale)
            actual_amount = Decimal('0')
            
            for item in sale_items:
                actual_amount += item.quantity * item.product.sale_price
            
            # Apply tax to get the total expected amount
            expected_amount_with_tax = actual_amount + (actual_amount * sale.tax)
            total_expected_amount += expected_amount_with_tax
            
            # Determine payment status based on amount received vs expected
            if sale.total_amount <= 0:
                # Unpaid sale
                credit_sales += expected_amount_with_tax
                unpaid_count += 1
            elif sale.total_amount < expected_amount_with_tax:
                # Partially paid sale
                cash_sales += sale.total_amount  # What was actually received
                credit_sales += (expected_amount_with_tax - sale.total_amount)  # Outstanding amount
                partially_paid_amount += sale.total_amount
                partially_paid_count += 1
            else:
                # Fully paid sale
                cash_sales += sale.total_amount
                fully_paid_count += 1
        
        # Get highest sale
        highest_sale = sales.aggregate(max_sale=Max('total_amount'))['max_sale'] or Decimal('0')
        
        # Get sale items
        sale_items = SaleItem.objects.filter(sale__in=sales)
        total_items = sale_items.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate average sale value
        avg_sale_received = Decimal('0')
        avg_sale_expected = Decimal('0')
        if sales.count() > 0:
            avg_sale_received = total_sales_amount_received / sales.count()
            avg_sale_expected = total_expected_amount / sales.count()
            
        # Get top selling products
        top_products = sale_items.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('product__sale_price'))
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
                    'amount_received': 0,
                    'amount_expected': 0,
                    'transaction_count': 0
                }
            
            # Calculate expected amount for this sale
            sale_items = SaleItem.objects.filter(sale=sale)
            actual_amount = Decimal('0')
            for item in sale_items:
                actual_amount += item.quantity * item.product.sale_price
            expected_amount_with_tax = actual_amount + (actual_amount * sale.tax)
            
            daily_sales[day]['amount_received'] += float(sale.total_amount)
            daily_sales[day]['amount_expected'] += float(expected_amount_with_tax)
            daily_sales[day]['transaction_count'] += 1
        
        daily_sales_list = list(daily_sales.values())
        
        # Calculate payment mode breakdown
        payment_mode_breakdown = {}
        for sale in sales:
            payment_mode_name = sale.payment_mode.name if sale.payment_mode else "Unspecified"
            if payment_mode_name not in payment_mode_breakdown:
                payment_mode_breakdown[payment_mode_name] = {
                    'amount_received': 0,
                    'transaction_count': 0
                }
            
            payment_mode_breakdown[payment_mode_name]['amount_received'] += float(sale.total_amount)
            payment_mode_breakdown[payment_mode_name]['transaction_count'] += 1
        
        payment_mode_list = [{"payment_mode": k, **v} for k, v in payment_mode_breakdown.items()]
        
        # Calculate collection efficiency
        collection_efficiency = Decimal('0')
        if total_expected_amount > 0:
            collection_efficiency = (total_sales_amount_received / total_expected_amount) * 100
        
        # Prepare comprehensive report response data
        report_data = {
            "title": f"Sales Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Sales performance from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            
            # Core Sales Metrics
            "total_amount_received": float(total_sales_amount_received),  # What was actually received
            "total_amount_expected": float(total_expected_amount),  # What should have been received
            "total_items_sold": total_items if total_items else 0,
            "average_sale_received": float(avg_sale_received),
            "average_sale_expected": float(avg_sale_expected),
            "highest_sale_value": float(highest_sale),
            
            # Payment Status Breakdown
            "cash_sales_amount": float(cash_sales),  # Fully paid amount
            "credit_sales_amount": float(credit_sales),  # Outstanding/unpaid amount
            "partially_paid_amount": float(partially_paid_amount),  # Amount received for partial payments
            
            # Transaction Count Breakdown
            "total_transactions": sales.count(),
            "fully_paid_transactions": fully_paid_count,
            "partially_paid_transactions": partially_paid_count,
            "unpaid_transactions": unpaid_count,
            
            # Analysis
            "collection_efficiency_percentage": float(collection_efficiency),
            "outstanding_amount": float(credit_sales),
            "top_selling_products": top_products_data,
            "daily_sales_breakdown": daily_sales_list,
            "payment_mode_breakdown": payment_mode_list
        }
        
        return Response(report_data, status=status.HTTP_200_OK)


class GenerateInventoryReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate an inventory report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH)
        ]
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
            "store": store.name,
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
        ]
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
        print('purchases',purchases, purchases.aggregate(total=Sum('total_amount')))
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
        gross_profit = (total_sales + total_payment_ins) - (total_purchases + total_payment_outs)
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
        ]
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
        print(customers)
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
                'customer_name': Customer.objects.get(id=item['customer']).name,
                'total_spent': float(item['total_spent']),
                'purchase_count': item['purchase_count'],
            })
        
        # Calculate retention rate
        retention_rate = Decimal('0')
        if total_customers > 0:
            retention_rate = (Decimal(returning_customer_count) / Decimal(total_customers)) * 100
        
        print('total_customers',total_customers)
        print('top_customers',top_customers)
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
        ]
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
            total_revenue=Sum(F('quantity') * F('product__sale_price'))
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
            total_revenue=Sum(F('quantity') * F('product__sale_price'))
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
        ]
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

        # REVENUE CALCULATION
        # 1. Get all money coming IN (Revenue streams)
        
        # Sales revenue from completed sales
        sales = Sale.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        sales_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Payment ins (money received - including from sales and other sources)
        payment_ins = PaymentIn.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_payment_ins = payment_ins.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # COSTS CALCULATION  
        # 2. Get all money going OUT (Cost streams)
        
        # Purchase costs (money spent on inventory/stock)
        purchases = Purchase.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        purchase_costs = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Payment outs (money paid out - including for purchases and other expenses)
        payment_outs = PaymentOut.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_payment_outs = payment_outs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Operating expenses (general business expenses)
        expenses = Expense.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        operating_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate Cost of Goods Sold (COGS) from sales items
        sale_items = SaleItem.objects.filter(sale__in=sales)
        cost_of_goods_sold = Decimal('0')
        
        for item in sale_items:
            try:
                # Use product's purchase price as the cost
                cost_of_goods_sold += item.quantity * item.product.purchase_price
            except:
                pass
        
        # PROFIT CALCULATIONS
        # Total Revenue = All money coming in
        total_revenue = total_payment_ins
        
        # Total Costs = All money going out + COGS
        total_costs = total_payment_outs + operating_expenses
        
        # Gross profit = Sales Revenue - COGS
        gross_profit = sales_revenue - cost_of_goods_sold
        
        # Net profit = Total Revenue - Total Costs
        net_profit = total_revenue - total_costs
        
        # Alternative net profit calculation for verification
        # Net profit = Sales Revenue - COGS - Operating Expenses - (Purchase Costs not yet sold)
        adjusted_net_profit = sales_revenue - cost_of_goods_sold - operating_expenses
        
        # Calculate profit margin based on sales revenue
        profit_margin = Decimal('0')
        if sales_revenue > 0:
            profit_margin = (gross_profit / sales_revenue) * 100
            
        net_profit_margin = Decimal('0')
        if total_revenue > 0:
            net_profit_margin = (net_profit / total_revenue) * 100
        
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
        
        # Calculate comprehensive daily profit trend
        profit_trend = {}
        
        # Daily revenue from payment ins
        daily_payment_ins = payment_ins.extra(select={'day': "date(created_at)"}).values('day').annotate(total=Sum('amount'))
        for entry in daily_payment_ins:
            day = entry['day'].strftime('%Y-%m-%d')
            if day not in profit_trend:
                profit_trend[day] = {
                    'date': day,
                    'revenue': 0,
                    'costs': 0,
                    'profit': 0
                }
            profit_trend[day]['revenue'] += float(entry['total'])
        
        # Daily costs from payment outs
        daily_payment_outs = payment_outs.extra(select={'day': "date(created_at)"}).values('day').annotate(total=Sum('amount'))
        for entry in daily_payment_outs:
            day = entry['day'].strftime('%Y-%m-%d')
            if day not in profit_trend:
                profit_trend[day] = {
                    'date': day,
                    'revenue': 0,
                    'costs': 0,
                    'profit': 0
                }
            profit_trend[day]['costs'] += float(entry['total'])
        
        # Daily expenses
        daily_expenses = expenses.extra(select={'day': "date(created_at)"}).values('day').annotate(total=Sum('amount'))
        for entry in daily_expenses:
            day = entry['day'].strftime('%Y-%m-%d')
            if day not in profit_trend:
                profit_trend[day] = {
                    'date': day,
                    'revenue': 0,
                    'costs': 0,
                    'profit': 0
                }
            profit_trend[day]['costs'] += float(entry['total'])
        
        # Calculate daily profit
        for day_data in profit_trend.values():
            day_data['profit'] = day_data['revenue'] - day_data['costs']
        
        # Convert to list for JSON storage
        profit_trend_list = list(profit_trend.values())
        
        # Financial health metrics
        payment_in_vs_out_ratio = Decimal('0')
        if total_payment_outs > 0:
            payment_in_vs_out_ratio = total_payment_ins / total_payment_outs
        
        # Prepare comprehensive report data
        report_data = {
            "title": f"Comprehensive Profit Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Comprehensive profit analysis including all financial transactions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            
            # Core Profit Metrics
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "adjusted_net_profit": float(adjusted_net_profit),
            "profit_margin_percentage": float(profit_margin),
            "net_profit_margin_percentage": float(net_profit_margin),
            
            # Revenue Breakdown
            "total_revenue": float(total_revenue),
            "sales_revenue": float(sales_revenue),
            "total_payment_ins": float(total_payment_ins),
            
            # Cost Breakdown
            "total_costs": float(total_costs),
            "cost_of_goods_sold": float(cost_of_goods_sold),
            "purchase_costs": float(purchase_costs),
            "operating_expenses": float(operating_expenses),
            "total_payment_outs": float(total_payment_outs),
            
            # Analysis
            "profit_by_product_category": profit_by_category_list,
            "profit_trend": profit_trend_list,
            
            # Financial Health Indicators
            "payment_in_vs_out_ratio": float(payment_in_vs_out_ratio),
            "total_transactions": sales.count() + purchases.count() + expenses.count(),
            "avg_daily_profit": float(net_profit / max(1, (end_date - start_date).days))
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
        ]
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


class GeneratePurchaseReportView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Generate a purchase report for a store",
        parameters=[
            OpenApiParameter(name='store_id', type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name='start_date', type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='end_date', type=str, location=OpenApiParameter.QUERY)
        ]
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
        
        # Get purchase data
        purchases = Purchase.objects.filter(
            store_id=store_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate comprehensive purchase metrics
        total_purchase_amount_paid = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Calculate actual expected amounts and payment status
        cash_purchases = Decimal('0')  # Fully paid purchases
        credit_purchases = Decimal('0')  # Outstanding amount from unpaid/partially paid purchases
        total_expected_amount = Decimal('0')  # Total amount that should have been paid
        partially_paid_amount = Decimal('0')  # Amount paid for partially paid purchases
        unpaid_count = 0
        partially_paid_count = 0
        fully_paid_count = 0
        
        for purchase in purchases:
            # Calculate the actual expected amount for this purchase (including tax)
            purchase_items = PurchaseItem.objects.filter(purchase=purchase)
            actual_amount = Decimal('0')
            
            for item in purchase_items:
                actual_amount += item.quantity * item.product.purchase_price
            
            # Apply tax to get the total expected amount
            expected_amount_with_tax = actual_amount + (actual_amount * purchase.tax)
            total_expected_amount += expected_amount_with_tax
            
            # Determine payment status based on amount paid vs expected
            if purchase.total_amount <= 0:
                # Unpaid purchase
                credit_purchases += expected_amount_with_tax
                unpaid_count += 1
            elif purchase.total_amount < expected_amount_with_tax:
                # Partially paid purchase
                cash_purchases += purchase.total_amount  # What was actually paid
                credit_purchases += (expected_amount_with_tax - purchase.total_amount)  # Outstanding amount
                partially_paid_amount += purchase.total_amount
                partially_paid_count += 1
            else:
                # Fully paid purchase
                cash_purchases += purchase.total_amount
                fully_paid_count += 1
        
        # Get highest purchase
        highest_purchase = purchases.aggregate(max_purchase=Max('total_amount'))['max_purchase'] or Decimal('0')
        
        # Get purchase items
        purchase_items = PurchaseItem.objects.filter(purchase__in=purchases)
        total_items = purchase_items.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate average purchase value
        avg_purchase_paid = Decimal('0')
        avg_purchase_expected = Decimal('0')
        if purchases.count() > 0:
            avg_purchase_paid = total_purchase_amount_paid / purchases.count()
            avg_purchase_expected = total_expected_amount / purchases.count()
            
        # Get top suppliers by purchase volume
        top_suppliers = purchases.values('supplier').annotate(
            total_amount=Sum('total_amount'),
            purchase_count=Count('id')
        ).order_by('-total_amount')[:10]
        
        top_suppliers_data = []
        for item in top_suppliers:
            try:
                supplier = Supplier.objects.get(pk=item['supplier'])
                top_suppliers_data.append({
                    'supplier_id': str(supplier.id),
                    'supplier_name': supplier.name,
                    'total_amount': float(item['total_amount']),
                    'purchase_count': item['purchase_count']
                })
            except:
                continue
        
        # Get top purchased products
        top_products = purchase_items.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_cost=Sum(F('quantity') * F('product__purchase_price'))
        ).order_by('-total_quantity')[:10]
        
        top_products_data = []
        for item in top_products:
            try:
                product = Product.objects.get(pk=item['product'])
                top_products_data.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'total_quantity': float(item['total_quantity']),
                    'total_cost': float(item.get('total_cost', 0))
                })
            except Product.DoesNotExist:
                continue
        
        # Calculate daily purchase breakdown
        daily_purchases = {}
        for purchase in purchases:
            day = purchase.created_at.strftime('%Y-%m-%d')
            if day not in daily_purchases:
                daily_purchases[day] = {
                    'date': day,
                    'amount_paid': 0,
                    'amount_expected': 0,
                    'transaction_count': 0
                }
            
            # Calculate expected amount for this purchase
            purchase_items = PurchaseItem.objects.filter(purchase=purchase)
            actual_amount = Decimal('0')
            for item in purchase_items:
                actual_amount += item.quantity * item.product.purchase_price
            expected_amount_with_tax = actual_amount + (actual_amount * purchase.tax)
            
            daily_purchases[day]['amount_paid'] += float(purchase.total_amount)
            daily_purchases[day]['amount_expected'] += float(expected_amount_with_tax)
            daily_purchases[day]['transaction_count'] += 1
        
        daily_purchases_list = list(daily_purchases.values())
        
        # Calculate payment mode breakdown
        payment_mode_breakdown = {}
        for purchase in purchases:
            payment_mode_name = purchase.payment_mode.name if purchase.payment_mode else "Unspecified"
            if payment_mode_name not in payment_mode_breakdown:
                payment_mode_breakdown[payment_mode_name] = {
                    'amount_paid': 0,
                    'transaction_count': 0
                }
            
            payment_mode_breakdown[payment_mode_name]['amount_paid'] += float(purchase.total_amount)
            payment_mode_breakdown[payment_mode_name]['transaction_count'] += 1
        
        payment_mode_list = [{"payment_mode": k, **v} for k, v in payment_mode_breakdown.items()]
        
        # Calculate purchase by product category
        category_breakdown = {}
        for item in purchase_items:
            try:
                category_name = item.product.product_category.name
                if category_name not in category_breakdown:
                    category_breakdown[category_name] = {
                        'quantity': 0,
                        'cost': 0
                    }
                
                category_breakdown[category_name]['quantity'] += float(item.quantity)
                category_breakdown[category_name]['cost'] += float(item.quantity * item.product.purchase_price)
            except:
                pass
        
        category_breakdown_list = [{"category": k, **v} for k, v in category_breakdown.items()]
        
        # Calculate payment efficiency
        payment_efficiency = Decimal('0')
        if total_expected_amount > 0:
            payment_efficiency = (total_purchase_amount_paid / total_expected_amount) * 100
        
        # Prepare comprehensive report response data
        report_data = {
            "title": f"Purchase Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "description": f"Purchase analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "store": store_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            
            # Core Purchase Metrics
            "total_amount_paid": float(total_purchase_amount_paid),  # What was actually paid
            "total_amount_expected": float(total_expected_amount),  # What should have been paid
            "total_items_purchased": total_items if total_items else 0,
            "average_purchase_paid": float(avg_purchase_paid),
            "average_purchase_expected": float(avg_purchase_expected),
            "highest_purchase_value": float(highest_purchase),
            
            # Payment Status Breakdown
            "cash_purchases_amount": float(cash_purchases),  # Fully paid amount
            "credit_purchases_amount": float(credit_purchases),  # Outstanding/unpaid amount
            "partially_paid_amount": float(partially_paid_amount),  # Amount paid for partial payments
            
            # Transaction Count Breakdown
            "total_transactions": purchases.count(),
            "fully_paid_transactions": fully_paid_count,
            "partially_paid_transactions": partially_paid_count,
            "unpaid_transactions": unpaid_count,
            
            # Analysis
            "payment_efficiency_percentage": float(payment_efficiency),
            "outstanding_amount": float(credit_purchases),
            "top_suppliers": top_suppliers_data,
            "top_purchased_products": top_products_data,
            "purchase_by_category": category_breakdown_list,
            "daily_purchase_breakdown": daily_purchases_list,
            "payment_mode_breakdown": payment_mode_list
        }
        
        return Response(report_data, status=status.HTTP_200_OK)
    