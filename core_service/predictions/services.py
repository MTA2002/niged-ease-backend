from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, F, Count
from transactions.models import Sale, SaleItem, Customer
from inventory.models import Product
from companies.models import Store, Company
import pandas as pd
from prophet import Prophet

def calculate_monthly_revenue(store_id: str, year: int, month: int) -> Decimal:
    """
    Calculate total revenue for a given store, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    revenue = SaleItem.objects.filter(
        sale__store_id=store_id,
        sale__created_at__gte=start_date,
        sale__created_at__lt=end_date
    ).select_related('product', 'sale').aggregate(
        total=Sum(F('quantity') * F('product__sale_price'))
    )['total']

    return Decimal('0.00') if revenue is None else revenue

def calculate_monthly_profit(store_id: str, year: int, month: int) -> Decimal:
    """
    Calculate total profit for a given store, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    profit = SaleItem.objects.filter(
        sale__store_id=store_id,
        sale__created_at__gte=start_date,
        sale__created_at__lt=end_date
    ).select_related('product', 'sale').aggregate(
        total=Sum(F('quantity') * (F('product__sale_price') - F('product__purchase_price')))
    )['total']

    return Decimal('0.00') if profit is None else profit

def calculate_monthly_customers(store_id: str, year: int, month: int) -> int:
    """
    Calculate total new customers for a given store, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    customer_count = Customer.objects.filter(
        store_id=store_id,
        created_at__gte=start_date,
        created_at__lt=end_date
    ).count()

    return customer_count

def calculate_company_monthly_revenue(company_id: str, year: int, month: int) -> Decimal:
    """
    Calculate total revenue for a given company, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    # Get all stores for this company
    stores = Store.objects.filter(company_id=company_id)
    store_ids = list(stores.values_list('id', flat=True))

    revenue = SaleItem.objects.filter(
        sale__store_id__in=store_ids,
        sale__created_at__gte=start_date,
        sale__created_at__lt=end_date
    ).select_related('product', 'sale').aggregate(
        total=Sum(F('quantity') * F('product__sale_price'))
    )['total']

    return Decimal('0.00') if revenue is None else revenue

def calculate_company_monthly_profit(company_id: str, year: int, month: int) -> Decimal:
    """
    Calculate total profit for a given company, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    # Get all stores for this company
    stores = Store.objects.filter(company_id=company_id)
    store_ids = list(stores.values_list('id', flat=True))

    profit = SaleItem.objects.filter(
        sale__store_id__in=store_ids,
        sale__created_at__gte=start_date,
        sale__created_at__lt=end_date
    ).select_related('product', 'sale').aggregate(
        total=Sum(F('quantity') * (F('product__sale_price') - F('product__purchase_price')))
    )['total']

    return Decimal('0.00') if profit is None else profit

def calculate_company_monthly_customers(company_id: str, year: int, month: int) -> int:
    """
    Calculate total new customers for a given company, year, and month.
    """
    start_date = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = timezone.make_aware(datetime(year, month + 1, 1))

    # Get all stores for this company
    stores = Store.objects.filter(company_id=company_id)
    store_ids = list(stores.values_list('id', flat=True))

    # Count customers for all stores in this company
    customer_count = Customer.objects.filter(
        store_id__in=store_ids,
        created_at__gte=start_date,
        created_at__lt=end_date
    ).count()

    return customer_count

def get_historical_monthly_data(identifier: str, metric_calculator_func: callable, num_months: int = 12, is_company: bool = False) -> list:
    """
    Retrieve historical data for the specified metric over the past num_months.
    Supports both store-level and company-level metrics.
    """
    current_date = timezone.now()
    historical_data = []

    # Validate identifier exists
    if is_company:
        if not Company.objects.filter(id=identifier).exists():
            raise ValueError(f"Company with ID {identifier} not found")
    else:
        if not Store.objects.filter(id=identifier).exists():
            raise ValueError(f"Store with ID {identifier} not found")

    for i in range(num_months):
        target_date = current_date - timedelta(days=30 * i)
        year = target_date.year
        month = target_date.month

        value = metric_calculator_func(identifier, year, month)
        historical_data.append({
            'date': f"{year}-{month:02d}-01",
            'value': value
        })

    return sorted(historical_data, key=lambda x: x['date'])

def predict_future_months(historical_data: list, num_future_periods: int, metric: str = 'revenue') -> tuple[list, str]:
    """
    Predict future values using Prophet if enough data is available, otherwise use a simple trend-based approach.
    Returns both predictions and the method used.
    """
    # Check if we have enough non-zero data points for Prophet
    non_zero_data = [d for d in historical_data if float(d['value']) > 0]
    
    if len(non_zero_data) >= 6:
        try:
            # Use Prophet for prediction
            df = pd.DataFrame([
                {'ds': pd.to_datetime(d['date']), 'y': float(d['value'])}
                for d in historical_data
            ])
            
            model = Prophet(
                seasonality_mode='additive',
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            model.fit(df)
            
            future = model.make_future_dataframe(periods=num_future_periods, freq='MS')
            forecast = model.predict(future)
            
            # Get only the future predictions
            future_predictions = forecast.tail(num_future_periods)
            
            predictions = [
                {
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_value': max(0, float(row['yhat']))  # Ensure non-negative predictions
                }
                for _, row in future_predictions.iterrows()
            ]
            return predictions, 'prophet'
        except Exception as e:
            # If Prophet fails, fall back to trend-based prediction
            return trend_based_prediction(historical_data, num_future_periods), 'trend_based'
    else:
        # Use trend-based prediction for small datasets
        return trend_based_prediction(historical_data, num_future_periods), 'trend_based'

def trend_based_prediction(historical_data: list, num_future_periods: int) -> list:
    """
    Make predictions based on simple trend analysis when there isn't enough data for Prophet.
    """
    if not historical_data:
        return []
    
    # Convert to numpy arrays for easier calculation
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in historical_data]
    values = [float(d['value']) for d in historical_data]
    
    # Calculate simple moving average and trend
    if len(values) > 1:
        # Calculate trend (average change per period)
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)
        
        # Use last known value and trend for prediction
        last_value = values[-1]
        last_date = dates[-1]
        
        predictions = []
        for i in range(num_future_periods):
            next_date = last_date + timedelta(days=30 * (i + 1))
            predicted_value = max(0, last_value + (avg_change * (i + 1)))  # Ensure non-negative
            predictions.append({
                'date': next_date.strftime('%Y-%m-%d'),
                'predicted_value': predicted_value
            })
    else:
        # If only one data point, use it as constant prediction
        last_value = values[0]
        last_date = dates[0]
        predictions = []
        for i in range(num_future_periods):
            next_date = last_date + timedelta(days=30 * (i + 1))
            predictions.append({
                'date': next_date.strftime('%Y-%m-%d'),
                'predicted_value': last_value
            })
    
    return predictions 