from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from .models import (
    PaymentMode, Currency, SubscriptionPlan, Company, Sale, SaleItem, Purchase, PurchaseItem,
    ExpenseCategory, Expense, Payable, Receivable, Bank, PaymentOut, PaymentIn, Report
)
from .serializers import (
    PaymentModeSerializer, CurrencySerializer, SubscriptionPlanSerializer, CompanySerializer,
    SaleSerializer, SaleItemSerializer, PurchaseSerializer, PurchaseItemSerializer,
    ExpenseCategorySerializer, ExpenseSerializer, PayableSerializer, ReceivableSerializer,
    BankSerializer, PaymentOutSerializer, PaymentInSerializer, ReportSerializer
)
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import uuid

 
class VerifyTokenPermission(IsAuthenticated): 
    def has_permission(self, request, view):
        request.user_id = 1
        request.company_id = 1
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
            request.company_id = data.get('company_id')
            request.user_id = data.get('user_id')
            if not request.company_id:
                raise PermissionDenied("No company_id in token")
            return True
        return False
    


class SignupView(APIView): 
    permission_classes = [AllowAny]  # Public endpoint for signup

    def post(self, request):
        print(request.data)
        company_name = request.data.get('company_name')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        # Check if a company with the same email already exists
        if Company.objects.filter(email=email).exists():
            return Response({"error": "A company with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create new company with auto-generated ID
        company = Company(
            id=uuid.uuid4(),  # Fresh UUID for new company
            name=company_name,
            email=email,
            is_active=True  # Active after receipt verification
        ) 
    
        company.save()

        # Create default admin user in User Management Service
        user_data = { 
            'company_id': str(company.id),
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,  # Plaintext password, hashed by UserSerializer
            'role': '70091b63-1edb-44cc-839c-a63e9906ebae',
            'is_staff': True
        }
        user_response = requests.post(
            'http://127.0.0.1:8001/users/',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        if user_response.status_code != 201:
            # Rollback company creation if user creation fails
            company.delete()
            return Response({
                "error": "Failed to create admin user",
                "details": user_response.json() if user_response.content else "No details available"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "company_id": str(company.id),
            "message": "Company created successfully. Log in with your email and password."
        }, status=status.HTTP_201_CREATED)

 
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        # Filter to only the company associated with the token
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        return self.queryset.filter(id=self.request.company_id)

    def perform_create(self, serializer):
        # This is for authenticated users creating additional companies (unlikely in SaaS signup)
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        
        # Verify receipt for this edge case (e.g., admin adding a sub-company)
        response = requests.post(
            'http://localhost:8002/verify-receipt',
            json=serializer.validated_data,  # Adjust based on what 8002 expects
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200 and response.json().get('valid'):
            serializer.save(id=uuid.uuid4())  # Generate new ID, not reuse request.company_id
        else:
            return Response({'error': 'Receipt verification failed'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        # Restrict deletion to admins
        token_response = requests.post(
            'http://127.0.0.1:8000/api/auth/verify-token/',
            json={'token': self.request.headers.get('Authorization', '').replace('Bearer ', '')},
            headers={'Content-Type': 'application/json'}
        )
        if token_response.status_code == 200 and token_response.json().get('role') == 'admin':
            instance.is_active = False  # Soft delete
            instance.save()
        else:
            raise PermissionDenied("Only admins can delete the company")
# Base class for tenant-filtered viewsets
class TenantFilteredViewSet(viewsets.ModelViewSet):
    permission_classes = [VerifyTokenPermission]

    def get_queryset(self):
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        # Filter by company_id (override in subclasses if needed)
        return self.queryset.filter(company_id=self.request.company_id)

    def perform_create(self, serializer):
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        serializer.save(company_id=self.request.company_id)

class PaymentModeViewSet(TenantFilteredViewSet):
    queryset = PaymentMode.objects.all()
    serializer_class = PaymentModeSerializer

class CurrencyViewSet(TenantFilteredViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class SubscriptionPlanViewSet(TenantFilteredViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class SaleViewSet(TenantFilteredViewSet): 
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class SaleItemViewSet(TenantFilteredViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer

    def get_queryset(self):
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        return self.queryset.filter(sale__company_id=self.request.company_id)  # Filter via Sale

class PurchaseViewSet(TenantFilteredViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class PurchaseItemViewSet(TenantFilteredViewSet): 
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer

    def get_queryset(self):
        company = Company.objects.get(id=self.request.company_id)
        if not company.is_active:
            raise PermissionDenied("Subscription inactive")
        return self.queryset.filter(purchase__company_id=self.request.company_id)  # Filter via Purchase

class ExpenseCategoryViewSet(TenantFilteredViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class ExpenseViewSet(TenantFilteredViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class PayableViewSet(TenantFilteredViewSet):
    queryset = Payable.objects.all()
    serializer_class = PayableSerializer

class ReceivableViewSet(TenantFilteredViewSet):
    queryset = Receivable.objects.all()
    serializer_class = ReceivableSerializer

class BankViewSet(TenantFilteredViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class PaymentOutViewSet(TenantFilteredViewSet):
    queryset = PaymentOut.objects.all()
    serializer_class = PaymentOutSerializer

class PaymentInViewSet(TenantFilteredViewSet):
    queryset = PaymentIn.objects.all()
    serializer_class = PaymentInSerializer

class ReportViewSet(TenantFilteredViewSet): 
    queryset = Report.objects.all()
    serializer_class = ReportSerializer