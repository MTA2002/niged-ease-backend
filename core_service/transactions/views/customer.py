# type: ignore
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from transactions.models.customer import Customer
from transactions.serializers.customer import CustomerSerializer
from companies.models.store import Store
from companies.models.company import Company


class CustomerListView(APIView):
    @extend_schema(
        description="Get a list of all customers for a specific store",
        responses={200: CustomerSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        customers = Customer.objects.filter(store_id=store_id)
        serializer = CustomerSerializer(customers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new customer for a specific store",
        request=CustomerSerializer,
        responses={
            201: CustomerSerializer,
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="Subscription limit reached")
        }
    )
    def post(self, request: Request, store_id):
        # Get the store and company to check subscription limits
        try:
            store = Store.objects.get(pk=store_id)
            company = store.company_id
            current_customer_count = Customer.objects.filter(store__company_id=company).count()
            
            if not company.check_subscription_limits('customers', current_customer_count):
                return Response(
                    {
                        'error': 'Subscription customer limit reached',
                        'current_count': current_customer_count,
                        'max_allowed': company.subscription_plan.max_customers if company.subscription_plan else 0
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Store.DoesNotExist:
            raise Http404


class CustomerDetailView(APIView):
    def get_customer(self, id, store_id):
        try:
            customer = Customer.objects.get(pk=id, store_id=store_id)
            return customer
        except Customer.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific customer by ID for a specific store",
        responses={
            200: CustomerSerializer,
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def get(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        serializer = CustomerSerializer(customer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a customer for a specific store",
        request=CustomerSerializer,
        responses={
            200: CustomerSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def put(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        request.data['store_id'] = store_id
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a customer for a specific store",
        responses={
            204: OpenApiResponse(description="Customer deleted successfully"),
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)