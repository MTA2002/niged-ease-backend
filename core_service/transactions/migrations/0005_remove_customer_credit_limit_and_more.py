# Generated by Django 5.1.7 on 2025-05-27 07:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_purchaseitem_item_purchase_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='credit_limit',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='credit_limit',
        ),
    ]
