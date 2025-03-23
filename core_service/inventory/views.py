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
        return True
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return False
        response = requests.post(
            'http://user-management-service:8000/api/auth/verify-token/',  # Adjust URL as needed
            json={'token': token},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            request.company_id = response.json().get('company_id')  # Assuming company_id is returned
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