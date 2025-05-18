from django.http import JsonResponse
from django.utils import timezone
from companies.models import Company

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip subscription check for unauthenticated requests
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip subscription check for admin users
        if request.user.is_staff:
            return self.get_response(request)

        # Get company from user's token
        company_id = getattr(request.user, 'company_id', None)
        if not company_id:
            return JsonResponse({
                'error': 'No company associated with this user'
            }, status=403)

        try:
            company = Company.objects.get(id=company_id)
            
            # Check if subscription is valid
            if not company.is_subscription_valid():
                return JsonResponse({
                    'error': 'Subscription has expired',
                    'expired_at': company.subscription_expiration_date.isoformat() if company.subscription_expiration_date else None
                }, status=403)

            # Add company to request for easy access in views
            request.company = company
            
        except Company.DoesNotExist:
            return JsonResponse({
                'error': 'Company not found'
            }, status=403)

        return self.get_response(request) 