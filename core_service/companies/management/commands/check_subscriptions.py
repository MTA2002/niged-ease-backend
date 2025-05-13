from django.core.management.base import BaseCommand
from django.utils import timezone
from companies.models import Subscription

class Command(BaseCommand):
    help = 'Checks for expired subscriptions and updates their status'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_subscriptions = Subscription.objects.filter(
            is_active=True,
            end_date__lt=now
        )

        for subscription in expired_subscriptions:
            subscription.is_active = False
            subscription.save()
            
            # Update company subscription status
            company = subscription.company
            company.is_subscribed = False
            company.save()
            
            self.stdout.write(
                self.style.WARNING(
                    f'Subscription expired for company: {company.name}'
                )
            ) 