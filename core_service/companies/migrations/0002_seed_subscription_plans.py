from django.db import migrations

def seed_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('companies', 'SubscriptionPlan')
    
    default_plans = [
        {
            'name': 'free',
            'description': 'Basic plan with limited features',
            'price': 0.00,
            'features': {
                'max_companies': 1,
                'max_stores': 2,
                'max_users': 1,
                'storage_limit_gb': 5
            }
        },
        {
            'name': 'standard',
            'description': 'Standard plan with moderate features',
            'price': 29.99,
            'features': {
                'max_companies': 3,
                'max_stores': 10,
                'max_users': 5,
                'storage_limit_gb': 20
            }
        },
        {
            'name': 'premium',
            'description': 'Premium plan with all features',
            'price': 99.99,
            'features': {
                'max_companies': 10,
                'max_stores': 50,
                'max_users': 20,
                'storage_limit_gb': 100
            }
        }
    ]
    
    for plan_data in default_plans:
        SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults={
                'description': plan_data['description'],
                'price': plan_data['price'],
                'features': plan_data['features']
            }
        )

def reverse_seed_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('companies', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(name__in=['free', 'standard', 'premium']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_subscription_plans, reverse_seed_subscription_plans),
    ] 