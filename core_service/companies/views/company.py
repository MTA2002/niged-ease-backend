from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models import Company
from companies.serializers.company import CompanySerializer


class CompanyListView(APIView):
    @extend_schema(
        description="Get a list of all companies",
        responses={200: CompanySerializer(many=True)}
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
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific company by ID",
        responses={
            200: CompanySerializer,
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
            404: OpenApiResponse(description="Company not found")
        }
    )
    def delete(self, request: Request, id):
        company = self.get_company(id)
        company.delete()
        return Response({'message': 'Company deleted successfully'}, status=status.HTTP_204_NO_CONTENT)