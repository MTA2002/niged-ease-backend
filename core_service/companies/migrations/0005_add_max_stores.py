from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0004_merge_20250512_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_stores',
            field=models.IntegerField(default=2),
        ),
        migrations.RunSQL(
            # Update existing plans with max_stores based on their name
            """
            UPDATE subscription_plans 
            SET max_stores = CASE 
                WHEN LOWER(name) = 'free' THEN 2
                WHEN LOWER(name) = 'standard' THEN 10
                WHEN LOWER(name) = 'premium' THEN 50
                ELSE 2
            END;
            """,
            # Reverse SQL (if needed)
            """
            UPDATE subscription_plans 
            SET max_stores = 2;
            """
        ),
    ] 