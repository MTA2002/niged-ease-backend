from django.core.management.base import BaseCommand
from companies.models import SubscriptionPlan
from django.db import connection

class Command(BaseCommand):
    help = 'Remove duplicate SubscriptionPlan rows by id, keeping only one for each duplicate id, and optionally truncate the table.'

    def add_arguments(self, parser):
        parser.add_argument('--truncate', action='store_true', help='Truncate the table after cleanup.')

    def handle(self, *args, **options):
        self.stdout.write('Finding duplicate SubscriptionPlan ids...')
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, COUNT(*) as count FROM companies_subscriptionplan GROUP BY id HAVING COUNT(*) > 1;
            ''')
            duplicates = cursor.fetchall()

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate ids found.'))
        else:
            for dup_id, count in duplicates:
                self.stdout.write(f'Cleaning up duplicates for id: {dup_id} (count: {count})')
                with connection.cursor() as cursor:
                    cursor.execute('''
                        DELETE FROM companies_subscriptionplan
                        WHERE id = %s
                        AND ctid NOT IN (
                            SELECT min(ctid)
                            FROM companies_subscriptionplan
                            WHERE id = %s
                        );
                    ''', [str(dup_id), str(dup_id)])
                    deleted = cursor.rowcount
                self.stdout.write(self.style.WARNING(f'Deleted {deleted} duplicate(s) for id: {dup_id}'))
            self.stdout.write(self.style.SUCCESS('Duplicate cleanup complete.'))

        if options['truncate']:
            self.stdout.write('Truncating the companies_subscriptionplan table...')
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE companies_subscriptionplan CASCADE;')
            self.stdout.write(self.style.SUCCESS('Table truncated.')) 