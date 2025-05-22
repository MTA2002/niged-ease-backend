from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Prefetch, F
from inventory.models.product import Product
from inventory.models.inventory import Inventory
from inventory.serializers.product_search import ProductSearchResultSerializer

class ProductSearchView(generics.ListAPIView):
    """
    View for searching products and showing their storage locations
    and inventory levels (only showing positive inventory counts).
    """
    serializer_class = ProductSearchResultSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get_queryset(self):
        """
        Return products based on search criteria and filter
        to include only those with positive inventory.
        """
        store_id = self.kwargs.get('store_id')
        search_term = self.request.GET.get('search', '')
        
        # Start with base queryset filtered by store
        queryset = Product.objects.filter(store_id=store_id)
        
        # Apply search filtering if a search term is provided
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        
        # We'll only include products that have positive inventory
        # Create a subquery to get products with positive inventory
        products_with_inventory = Inventory.objects.filter(
            product=F('id'),
            quantity__gt=0
        ).values('product')
        
        # Filter to only include products with positive inventory
        queryset = queryset.filter(id__in=products_with_inventory)
        
        return queryset.distinct() 