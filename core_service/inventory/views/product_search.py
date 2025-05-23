from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Prefetch, F
from inventory.models.product import Product
from inventory.models.inventory import Inventory
from companies.models.store import Store
from inventory.serializers.product_search import ProductSearchResultSerializer

class ProductSearchView(generics.ListAPIView):
    """
    View for searching products across all stores within a company
    and showing their storage locations and inventory levels 
    (only showing positive inventory counts).
    """
    serializer_class = ProductSearchResultSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get_queryset(self):
        """
        Return products based on search criteria across all stores in a company
        and filter to include only those with positive inventory.
        """
        company_id = self.kwargs.get('company_id')
        
        # Get search term from URL path if available, otherwise from query parameters
        search_term = self.kwargs.get('search_term', '')
        if not search_term:
            search_term = self.request.GET.get('search', '')
        
        # Get all stores for this company
        store_ids = Store.objects.filter(company_id=company_id).values_list('id', flat=True)
        
        # Start with base queryset filtered by stores in this company
        queryset = Product.objects.filter(store_id__in=store_ids)
        
        # Apply search filtering if a search term is provided
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        
        # We'll only include products that have positive inventory
        # Join with inventory to filter products with positive inventory
        products_with_inventory = Inventory.objects.filter(
            product__in=queryset,
            quantity__gt=0
        ).values_list('product_id', flat=True)
        
        # Filter to only include products with positive inventory
        queryset = queryset.filter(id__in=products_with_inventory)
        
        return queryset.distinct() 