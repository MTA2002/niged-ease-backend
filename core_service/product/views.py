from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import ProductUnit, ProductCategory, Product
from .serializers import ProductUnitSerializer, ProductCategorySerializer, ProductSerializer
import requests
from rest_framework.response import Response
from rest_framework import status

class VerifyTokenPermission(IsAuthenticated):
    def has_permission(self, request, view):
        request.company_id = 1
        return True

class ProductUnitViewSet(viewsets.ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer
    permission_classes = [VerifyTokenPermission]
    def get_queryset(self):
        return self.queryset.filter(company_id=self.request.company_id)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [VerifyTokenPermission]
    def get_queryset(self):
        return self.queryset.filter(company_id=self.request.company_id)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [VerifyTokenPermission]
    def get_queryset(self):
        self.company_id = self.request.company_id
        return self.queryset.filter(company_id=self.company_id)
    def perform_create(self, serializer):
        serializer.save(company_id=self.company_id)
    def perform_update(self, serializer):
        serializer.save(company_id=self.company_id)