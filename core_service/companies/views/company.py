from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from companies.models import Company, SubscriptionPlan
from companies.serializers.company import CompanySerializer


class CompanyListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all companies",
        responses={200: CompanySerializer(many=True)}
    )
    def get(self, request: Request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new company",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'short_name', 'address', 'subscription_plan_id', 'currency_id'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'short_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company short name'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Company address'),
                'subscription_plan_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Subscription plan ID'),
                'currency_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Currency ID'),
            },
        ),
        responses={
            201: CompanySerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDetailView(APIView):
    def get_company(self, id):
        try:
            company = Company.objects.get(pk=id)
            return company
        except Company.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific company by ID",
        responses={
            200: CompanySerializer,
            404: "Company not found"
        }
    )
    def get(self, request: Request, id):
        company = self.get_company(id)
        serializer = CompanySerializer(company)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a company",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'short_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company short name'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Company address'),
                'subscription_plan_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Subscription plan ID'),
                'currency_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Currency ID'),
            },
        ),
        responses={
            200: CompanySerializer,
            400: "Invalid data",
            404: "Company not found"
        }
    )
    def put(self, request: Request, id):
        company = self.get_company(id)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a company",
        responses={
            204: "Company deleted",
            404: "Company not found"
        }
    )
    def delete(self, request: Request, id):
        company = self.get_company(id)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

