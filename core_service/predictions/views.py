from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Store, Company
from .services import (
    calculate_monthly_revenue,
    calculate_monthly_profit,
    calculate_monthly_customers,
    calculate_company_monthly_revenue,
    calculate_company_monthly_profit,
    calculate_company_monthly_customers,
    get_historical_monthly_data,
    predict_future_months
)

# Create your views here.

class RevenuePredictionAPIView(APIView):
    def post(self, request, store_id):
        # Validate store exists
        if not Store.objects.filter(id=store_id).exists():
            return Response(
                {'error': 'Store not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get parameters with defaults
        num_projection_months = request.data.get('num_projection_months', 6)
        num_historical_months = request.data.get('num_historical_months', 12)

        # Validate parameters
        if num_projection_months < 1 or num_historical_months < 1:
            return Response(
                {'error': 'Number of months must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get historical data
        historical_data = get_historical_monthly_data(
            store_id,
            calculate_monthly_revenue,
            num_historical_months
        )

        # Generate predictions
        predictions = predict_future_months(historical_data, num_projection_months)

        # Determine projection method based on data availability
        non_zero_data = [d for d in historical_data if float(d['value']) > 0]
        projection_method = 'prophet' if len(non_zero_data) >= 6 else 'trend_based'

        return Response({
            'store_id': store_id,
            'metric_predicted': 'revenue',
            'projection_method': projection_method,
            'num_projected_months': num_projection_months,
            'projections': predictions
        })

class ProfitPredictionAPIView(APIView):
    def post(self, request, store_id):
        # Validate store exists
        if not Store.objects.filter(id=store_id).exists():
            return Response(
                {'error': 'Store not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get parameters with defaults
        num_projection_months = request.data.get('num_projection_months', 6)
        num_historical_months = request.data.get('num_historical_months', 12)

        # Validate parameters
        if num_projection_months < 1 or num_historical_months < 1:
            return Response(
                {'error': 'Number of months must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get historical data
        historical_data = get_historical_monthly_data(
            store_id,
            calculate_monthly_profit,
            num_historical_months
        )

        # Generate predictions
        predictions = predict_future_months(historical_data, num_projection_months)

        # Determine projection method based on data availability
        non_zero_data = [d for d in historical_data if float(d['value']) > 0]
        projection_method = 'prophet' if len(non_zero_data) >= 6 else 'trend_based'

        return Response({
            'store_id': store_id,
            'metric_predicted': 'profit',
            'projection_method': projection_method,
            'num_projected_months': num_projection_months,
            'projections': predictions
        })

class CustomerPredictionAPIView(APIView):
    def post(self, request, store_id):
        # Validate store exists
        if not Store.objects.filter(id=store_id).exists():
            return Response(
                {'error': 'Store not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get parameters with defaults
        num_projection_months = request.data.get('num_projection_months', 6)
        num_historical_months = request.data.get('num_historical_months', 12)

        # Validate parameters
        if num_projection_months < 1 or num_historical_months < 1:
            return Response(
                {'error': 'Number of months must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get historical data
        historical_data = get_historical_monthly_data(
            store_id,
            calculate_monthly_customers,
            num_historical_months
        )

        # Generate predictions
        predictions, projection_method = predict_future_months(
            historical_data,
            num_projection_months,
            metric='customers'
        )

        return Response({
            'store_id': store_id,
            'metric_predicted': 'customers',
            'projection_method': projection_method,
            'num_projected_months': num_projection_months,
            'projections': predictions
        })

class CompanyRevenuePredictionAPIView(APIView):
    def post(self, request, company_id):
        try:
            # Get parameters with defaults
            num_projection_months = request.data.get('num_projection_months', 6)
            num_historical_months = request.data.get('num_historical_months', 12)

            # Validate parameters
            if num_projection_months < 1 or num_historical_months < 1:
                return Response(
                    {'error': 'Number of months must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get historical data
            historical_data = get_historical_monthly_data(
                company_id,
                calculate_company_monthly_revenue,
                num_historical_months,
                is_company=True
            )

            # Generate predictions
            predictions, projection_method = predict_future_months(
                historical_data,
                num_projection_months,
                metric='revenue'
            )

            return Response({
                'company_id': company_id,
                'metric_predicted': 'revenue',
                'projection_method': projection_method,
                'num_projected_months': num_projection_months,
                'projections': predictions
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

class CompanyProfitPredictionAPIView(APIView):
    def post(self, request, company_id):
        try:
            # Get parameters with defaults
            num_projection_months = request.data.get('num_projection_months', 6)
            num_historical_months = request.data.get('num_historical_months', 12)

            # Validate parameters
            if num_projection_months < 1 or num_historical_months < 1:
                return Response(
                    {'error': 'Number of months must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get historical data
            historical_data = get_historical_monthly_data(
                company_id,
                calculate_company_monthly_profit,
                num_historical_months,
                is_company=True
            )

            # Generate predictions
            predictions, projection_method = predict_future_months(
                historical_data,
                num_projection_months,
                metric='profit'
            )

            return Response({
                'company_id': company_id,
                'metric_predicted': 'profit',
                'projection_method': projection_method,
                'num_projected_months': num_projection_months,
                'projections': predictions
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

class CompanyCustomerPredictionAPIView(APIView):
    def post(self, request, company_id):
        try:
            # Get parameters with defaults
            num_projection_months = request.data.get('num_projection_months', 6)
            num_historical_months = request.data.get('num_historical_months', 12)

            # Validate parameters
            if num_projection_months < 1 or num_historical_months < 1:
                return Response(
                    {'error': 'Number of months must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get historical data
            historical_data = get_historical_monthly_data(
                company_id,
                calculate_company_monthly_customers,
                num_historical_months,
                is_company=True
            )

            # Generate predictions
            predictions, projection_method = predict_future_months(
                historical_data,
                num_projection_months,
                metric='customers'
            )

            return Response({
                'company_id': company_id,
                'metric_predicted': 'customers',
                'projection_method': projection_method,
                'num_projected_months': num_projection_months,
                'projections': predictions
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
