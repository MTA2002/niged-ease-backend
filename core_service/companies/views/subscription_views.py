from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Company, Subscription
from .serializers import SubscriptionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_subscription(request):
    """Check if a company is subscribed and return current plan details"""
    company = get_object_or_404(Company, id=request.user.company.id)
    
    if not company.is_subscribed or not company.current_subscription:
        return Response({
            'is_subscribed': False,
            'message': 'No active subscription'
        })
    
    subscription = company.current_subscription
    return Response({
        'is_subscribed': True,
        'subscription': SubscriptionSerializer(subscription).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def renew_subscription(request):
    """Admin endpoint to renew a subscription"""
    company_id = request.data.get('company_id')
    months = int(request.data.get('months', 1))
    
    company = get_object_or_404(Company, id=company_id)
    subscription = get_object_or_404(Subscription, company=company, is_active=True)
    
    subscription.renew(months=months)
    
    return Response({
        'message': f'Subscription renewed for {months} month(s)',
        'subscription': SubscriptionSerializer(subscription).data
    }) 