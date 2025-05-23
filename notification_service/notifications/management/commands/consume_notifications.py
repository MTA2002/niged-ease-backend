from django.core.management.base import BaseCommand
from notifications.services import RabbitMQConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start consuming notification messages from CloudAMQP'

    def handle(self, *args, **options):
        consumer = RabbitMQConsumer()
        
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 Starting notification consumer...')
            )
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('⏹️  Stopping consumer...')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Consumer error: {e}')
            )
            logger.error(f'Consumer error: {e}')
        finally:
            consumer.close()
            self.stdout.write(
                self.style.SUCCESS('✅ Consumer stopped')
            )