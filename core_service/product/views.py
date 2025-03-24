from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ProductUnit, ProductCategory, Product
from .serializers import ProductUnitSerializer, ProductCategorySerializer, ProductSerializer
import requests
from rest_framework.response import Response
from rest_framework import status

class VerifyTokenPermission(IsAuthenticated):
    def has_permission(self, request, view):
        request.company_id = "72527190-f935-4f91-be61-ae11c50b9fcb" # Default company_id for testing
        return True
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token: 
            return False
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/verify-token/',  # User Management Service
            json={'token': token},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            request.company_id = data.get('company_id')  # Set company_id from token
            if not request.company_id:
                raise PermissionDenied("No company_id in token")
            return True
        return False

class ProductUnitViewSet(viewsets.ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        # Filter by company_id from the token
        return self.queryset.filter(company_id=self.request.company_id)

    def perform_create(self, serializer):
        # Save with company_id from the token
        serializer.save(company_id=self.request.company_id)
         
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        return self.queryset.filter(company_id=self.request.company_id)

    def perform_create(self, serializer):
        # Always use company_id from token, ignoring payload company_id
        serializer.save(company_id=self.request.company_id)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        # Filter by company_id from the token
        return self.queryset.filter(company_id=self.request.company_id)

    def perform_create(self, serializer):
        # Save with company_id from the token
        serializer.save(company_id=self.request.company_id)