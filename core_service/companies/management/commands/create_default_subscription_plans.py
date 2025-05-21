from django.core.management.base import BaseCommand
from companies.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Creates default subscription plans'

    def handle(self, *args, **options):
        default_plans = SubscriptionPlan.get_default_plans()
        
        for plan_data in default_plans:
            # Create both monthly and yearly versions of each plan
            for billing_cycle in ['monthly', 'yearly']:
                # Adjust price for yearly plans (10 months for the price of 12)
                price = plan_data['price']
                if billing_cycle == 'yearly':
                    price = price * 10  # 10 months for the price of 12
                
                # Set duration based on billing cycle
                duration = 1 if billing_cycle == 'monthly' else 12
                
                plan, created = SubscriptionPlan.objects.get_or_create(
                    name=f"{plan_data['name']} ({billing_cycle})",
                    defaults={
                        'description': plan_data['description'],
                        'price': price,
                        'billing_cycle': billing_cycle,
                        'features': plan_data['features'],
                        'duration_in_months': duration,
                        'max_products': plan_data['features']['max_products'],
                        'max_stores': plan_data['features']['max_stores'],
                        'max_customers': plan_data['features']['max_customers'],
                        'storage_limit_gb': plan_data['features']['storage_limit_gb']
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created subscription plan: {plan.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Subscription plan already exists: {plan.name}'
                        )
                    ) 