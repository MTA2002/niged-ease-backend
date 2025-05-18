from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models import Company
from companies.serializers.company import CompanySerializer
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CompanyListView(APIView):
    @extend_schema(
        description="Get a list of all companies",
        responses={
            200: CompanySerializer(many=True),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def get(self, request: Request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new company",
        request=CompanySerializer,
        responses={
            201: CompanySerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def post(self, request: Request):
        logger.info(f"Received data: {request.data}")
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            logger.info(f"Validated data: {serializer.validated_data}")
            company = serializer.save()
            logger.info(f"Created company: {company.id}")
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDetailView(APIView):
    def get_company(self, id):
        try:
            company = Company.objects.get(pk=id)
            return company
        except Company.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific company by ID",
        responses={
            200: CompanySerializer,
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Company not found")
        }
    )
    def get(self, request: Request, id):
        company = self.get_company(id)
        serializer = CompanySerializer(company)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a company",
        request=CompanySerializer,
        responses={
            200: CompanySerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Company not found")
        }
    )
    def put(self, request: Request, id):
        company = self.get_company(id)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a company",
        responses={
            204: OpenApiResponse(description="Company deleted successfully"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Company not found")
        }
    )
    def delete(self, request: Request, id):
        company = self.get_company(id)
        company.delete()
        return Response({'message': 'Company deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class CompanySubscriptionCheckView(APIView):
    @extend_schema(
        description="Check if a company's subscription is valid",
        responses={
            200: OpenApiResponse(description="Subscription status retrieved successfully"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Company not found")
        }
    )
    def get(self, request: Request, id):
        try:
            company = Company.objects.get(pk=id)
        except Company.DoesNotExist:
            raise Http404
            
        is_valid = company.is_subscription_valid()
        
        response_data = {
            'is_valid': is_valid,
            'subscription_plan': company.subscription_plan.name if company.subscription_plan else None,
            'expiration_date': company.subscription_expiration_date,
            'days_remaining': (company.subscription_expiration_date - timezone.now()).days if company.subscription_expiration_date else 0
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class CompanySubscriptionRenewView(APIView):
    @extend_schema(
        description="Renew a company's subscription",
        request=OpenApiResponse(description="Optional months parameter"),
        responses={
            200: OpenApiResponse(description="Subscription renewed successfully"),
            400: OpenApiResponse(description="Invalid months value"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Company not found")
        }
    )
    def post(self, request: Request, id):
        try:
            company = Company.objects.get(pk=id)
        except Company.DoesNotExist:
            raise Http404
            
        # Get months from request, default to subscription plan's duration
        months = request.data.get('months')
        
        try:
            if months:
                months = int(months)
                if months <= 0:
                    return Response(
                        {'error': 'Months must be a positive number'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            success = company.renew_subscription(months)
            
            if success:
                return Response({
                    'message': 'Subscription renewed successfully',
                    'new_expiration_date': company.subscription_expiration_date,
                    'subscription_plan': company.subscription_plan.name if company.subscription_plan else None
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to renew subscription'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError:
            return Response(
                {'error': 'Invalid months value'},
                status=status.HTTP_400_BAD_REQUEST
            )