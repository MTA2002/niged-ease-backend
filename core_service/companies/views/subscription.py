from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models import Company
from companies.serializers import CompanySerializer

class CheckSubscriptionView(GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description='Subscription status retrieved successfully',
                response=CompanySerializer
            ),
            403: OpenApiResponse(
                description='Subscription has expired or is invalid'
            )
        },
        description='Check if a company\'s subscription is valid'
    )
    def get(self, request):
        """Check if a company's subscription is valid"""
        company = getattr(request, 'company', None)
        if not company:
            return Response({
                'error': 'No company associated with this user'
            }, status=status.HTTP_403_FORBIDDEN)

        if not company.is_subscription_valid():
            return Response({
                'is_valid': False,
                'message': 'Subscription has expired',
                'expired_at': company.subscription_expiration_date.isoformat() if company.subscription_expiration_date else None
            }, status=status.HTTP_403_FORBIDDEN)

        subscription_plan = company.subscription_plan
        return Response({
            'is_valid': True,
            'company': self.get_serializer(company).data,
            'subscription_details': {
                'start_date': company.subscription_start_date.isoformat() if company.subscription_start_date else None,
                'expiration_date': company.subscription_expiration_date.isoformat() if company.subscription_expiration_date else None,
                'plan': {
                    'id': subscription_plan.id,
                    'name': subscription_plan.name,
                    'max_products': subscription_plan.max_products,
                    'max_stores': subscription_plan.max_stores,
                    'max_users': subscription_plan.max_users,
                    'duration_in_months': subscription_plan.duration_in_months
                } if subscription_plan else None
            }
        }) 