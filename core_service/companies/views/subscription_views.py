from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from companies.models import Company, Subscription
from companies.serializers import SubscriptionSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

class CheckSubscriptionView(GenericAPIView): 
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Company ID to check subscription status',
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Subscription status retrieved successfully',
                response=SubscriptionSerializer
            ),
            400: OpenApiResponse(
                description='Company ID is required'
            ),
            404: OpenApiResponse(
                description='Company not found'
            )
        },
        description='Check if a company is subscribed and return current plan details'
    )
    def get(self, request):
        """Check if a company is subscribed and return current plan details"""
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response({
                'error': 'company_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        company = get_object_or_404(Company, id=company_id)
        
        if not company.is_subscribed or not company.current_subscription:
            return Response({
                'is_subscribed': False,
                'message': 'No active subscription'
            })
        
        subscription = company.current_subscription
        return Response({
            'is_subscribed': True,
            'subscription': self.get_serializer(subscription).data
        })

class RenewSubscriptionView(GenericAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'company_id': {'type': 'string', 'format': 'uuid'},
                    'months': {'type': 'integer', 'minimum': 1, 'default': 1}
                },
                'required': ['company_id']
            }
        },
        responses={
            200: OpenApiResponse(
                description='Subscription renewed successfully',
                response=SubscriptionSerializer
            ),
            400: OpenApiResponse(
                description='Invalid request data'
            ),
            404: OpenApiResponse(
                description='Company or subscription not found'
            )
        },
        description='Admin endpoint to renew a subscription'
    )
    def post(self, request):
        """Admin endpoint to renew a subscription"""
        company_id = request.data.get('company_id')
        months = int(request.data.get('months', 1))
        
        company = get_object_or_404(Company, id=company_id)
        subscription = get_object_or_404(Subscription, company=company, is_active=True)
        
        subscription.renew(months=months)
        
        return Response({
            'message': f'Subscription renewed for {months} month(s)',
            'subscription': self.get_serializer(subscription).data
        }) 



