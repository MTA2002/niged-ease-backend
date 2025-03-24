from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Store, Inventory
from .serializers import StoreSerializer, InventorySerializer
import requests
from rest_framework.response import Response
from rest_framework import status

class VerifyTokenPermission(IsAuthenticated):
    def has_permission(self, request, view):
        # Remove default company_id for testing in production
        request.company_id = "72527190-f935-4f91-be61-ae11c50b9fcb"  # Comment out or remove
        return True
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return False
        response = requests.post(
            'http://user-management-service:8000/api/auth/verify-token/',
            json={'token': token},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            company_id = data.get('company_id')
            if not company_id:
                return False
            from financial.models import Company
            if not Company.objects.filter(id=company_id).exists():
                return False
            request.company_id = company_id
            return True
        return False

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        return self.queryset.filter(company_id=self.request.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.company_id)

    def perform_update(self, serializer):
        serializer.save(company_id=self.request.company_id)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        return self.queryset.filter(store__company_id=self.request.company_id)

    def perform_create(self, serializer):
        serializer.save()  # No direct company_id, handled via store

    def perform_update(self, serializer):
        serializer.save()