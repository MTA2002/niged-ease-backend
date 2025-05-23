import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from companies.models import Store
from inventory.models import Product, ProductCategory, ProductUnit
from transactions.models import Sale, SaleItem, Customer
from clothings.models import Color, Collection, Season

class Command(BaseCommand):
    help = 'Seeds sample sales data for testing predictions'

    def add_arguments(self, parser):
        parser.add_argument('store_id', type=str, help='UUID of the store')
        parser.add_argument('--months', type=int, default=12, help='Number of months to generate data for')

    def handle(self, *args, **options):
        store_id = options['store_id']
        months = options['months']

        # Validate store exists
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Store with ID {store_id} not found'))
            return

        # Create required related objects if they don't exist
        # Create a product category
        category, _ = ProductCategory.objects.get_or_create(
            store_id=store,
            name='Sample Category',
            defaults={'description': 'Sample category for testing'}
        )

        # Create a product unit
        unit, _ = ProductUnit.objects.get_or_create(
            store_id=store,
            name='Piece',
            defaults={'description': 'Individual piece'}
        )

        # Create a color
        color, _ = Color.objects.get_or_create(
            store_id=store,
            name='Black',
            color_code='#000000',
            defaults={'description': 'Basic black color'}
        )

        # Create a season
        season, _ = Season.objects.get_or_create(
            store_id=store,
            name='Spring 2024',
            defaults={
                'start_date': datetime(2024, 3, 1).date(),
                'end_date': datetime(2024, 5, 31).date(),
                'description': 'Spring season 2024'
            }
        )

        # Create a collection
        collection, _ = Collection.objects.get_or_create(
            store_id=store,
            season_id=season,
            name='Basic Collection',
            defaults={
                'release_date': datetime(2024, 3, 1).date(),
                'description': 'Basic collection for testing'
            }
        )

        # Check/create products
        products = list(Product.objects.filter(store_id=store_id))
        if len(products) < 5:
            self.stdout.write('Creating sample products...')
            for i in range(5):
                purchase_price = Decimal(str(random.randint(5, 50)))
                sale_price = Decimal(str(random.randint(10, 100)))
                product = Product.objects.create(
                    store_id=store,
                    color_id=color,
                    collection_id=collection,
                    name=f'Sample Product {i+1}',
                    description=f'Sample product {i+1} for testing',
                    product_unit=unit,
                    product_category=category,
                    purchase_price=purchase_price,
                    sale_price=sale_price
                )
                products.append(product)

        # Generate sales data
        current_date = timezone.now()
        total_sales = 0
        total_customers = 0

        for i in range(months):
            month_start = current_date - timedelta(days=30 * i)
            month_end = month_start - timedelta(days=30)

            # Generate 10-20 customers per month
            num_customers = random.randint(10, 20)
            customers = []
            for j in range(num_customers):
                # Random timestamp within the month
                customer_date = month_end + timedelta(
                    seconds=random.randint(0, int((month_start - month_end).total_seconds()))
                )
                customer = Customer.objects.create(
                    store_id=store,
                    name=f'Customer {total_customers + j + 1}',
                    email=f'customer_{total_customers + j + 1}_{store_id}@example.com',
                    phone=f'+1234567890{total_customers + j + 1}'
                )
                customers.append(customer)
            total_customers += num_customers

            # Generate 20-50 sales per month
            num_sales = random.randint(20, 50)
            total_sales += num_sales

            for _ in range(num_sales):
                # Random timestamp within the month
                sale_date = month_end + timedelta(
                    seconds=random.randint(0, int((month_start - month_end).total_seconds()))
                )

                # Select a random customer
                customer = random.choice(customers)

                # Prepare sale items first to calculate total_amount
                num_items = random.randint(1, 5)
                sale_items = []
                total_amount = Decimal('0.00')
                for _ in range(num_items):
                    product = random.choice(products)
                    quantity = Decimal(str(random.randint(1, 5)))
                    item_amount = quantity * product.sale_price
                    total_amount += item_amount
                    sale_items.append((product, quantity))

                # Create sale with total_amount
                sale = Sale.objects.create(
                    store_id=store,
                    customer=customer,
                    created_at=sale_date,
                    total_amount=total_amount
                )

                # Create SaleItems
                for product, quantity in sale_items:
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        created_at=sale_date
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {total_customers} customers and {total_sales} sales for store {store_id} over {months} months'
            )
        ) 