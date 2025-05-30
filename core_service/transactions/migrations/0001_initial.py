# Generated by Django 5.1.7 on 2025-05-23 15:24

import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.store')),
            ],
            options={
                'db_table': 'customers',
            },
        ),
        migrations.CreateModel(
            name='PaymentMode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.store')),
            ],
            options={
                'db_table': 'payment_modes',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('tax', models.DecimalField(decimal_places=4, default=Decimal('0.00'), max_digits=19)),
                ('status', models.CharField(choices=[('UNPAID', 'Unpaid'), ('PARTIALLY_PAID', 'Partially Paid'), ('PAID', 'Paid')], default='UNPAID', max_length=15)),
                ('is_credit', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.currency')),
                ('payment_mode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='transactions.paymentmode')),
                ('store_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.store')),
            ],
            options={
                'db_table': 'purchases',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=19)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_items', to='inventory.product')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='transactions.purchase')),
            ],
            options={
                'db_table': 'purchase_items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('tax', models.DecimalField(decimal_places=4, default=Decimal('0.00'), max_digits=19)),
                ('is_credit', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('UNPAID', 'Unpaid'), ('PARTIALLY_PAID', 'Partially Paid'), ('PAID', 'Paid')], default='UNPAID', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.currency')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.customer')),
                ('payment_mode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='transactions.paymentmode')),
                ('store_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.store')),
            ],
            options={
                'db_table': 'sales',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=19)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_items', to='inventory.product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='transactions.sale')),
            ],
            options={
                'db_table': 'sale_items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.store')),
            ],
            options={
                'db_table': 'suppliers',
            },
        ),
        migrations.AddField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.supplier'),
        ),
    ]
