from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_products',
            field=models.IntegerField(default=100),
        ),
        migrations.RunSQL(
            # Update existing plans with max_products based on their name
            """
            UPDATE subscription_plans 
            SET max_products = CASE 
                WHEN LOWER(name) = 'free' THEN 50
                WHEN LOWER(name) = 'standard' THEN 500
                WHEN LOWER(name) = 'premium' THEN 5000
                ELSE 100
            END;
            """,
            # Reverse SQL (if needed)
            """
            UPDATE subscription_plans 
            SET max_products = 100;
            """
        ),
    ] 