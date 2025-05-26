from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models.store import Store
from companies.serializers.store import StoreSerializer
from companies.models.company import Company


class StoreListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Get a list of all stores",
        responses={200: StoreSerializer(many=True)}
    )
    def get(self, request: Request, company_id):
        stores = Store.objects.filter(company_id=company_id)
        serializer = StoreSerializer(stores, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new store",
        request=StoreSerializer,
        responses={
            201: StoreSerializer,
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="Subscription limit reached")
        }
    )
    def post(self, request: Request, company_id):
        # Get the company and check subscription limits
        try:
            company = Company.objects.get(pk=company_id)
            current_store_count = Store.objects.filter(company_id=company_id).count()
            
            if current_store_count >= company.subscription_plan.max_stores:# type: ignore

                return Response(
                    {
                        'error': 'Subscription store limit reached',
                        'current_count': current_store_count,
                        'max_allowed': company.subscription_plan.max_stores if company.subscription_plan else 0
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = StoreSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Company.DoesNotExist:
            raise Http404


class StoreDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get_store(self, company_id, id):
        try:
            store = Store.objects.get(pk=id, company_id=company_id)
            return store
        except Store.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific store by ID",
        responses={
            200: StoreSerializer,
            404: OpenApiResponse(description="Store not found")
        }
    )
    def get(self, request: Request, company_id, id):
        store = self.get_store(company_id, id)
        serializer = StoreSerializer(store)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a store",
        request=StoreSerializer,
        responses={
            200: StoreSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Store not found")
        }
    )
    def put(self, request: Request, company_id, id):
        store = self.get_store(company_id, id)
        
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a store",
        responses={
            204: OpenApiResponse(description="Store deleted successfully"),
            404: OpenApiResponse(description="Store not found")
        }
    )
    def delete(self, request: Request, company_id, id):
        store = self.get_store(company_id, id)
        store.delete()
        return Response({'message': 'Store deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 