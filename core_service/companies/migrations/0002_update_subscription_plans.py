from django.db import migrations

def update_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('companies', 'SubscriptionPlan')
    
    # Update existing plans
    plans = SubscriptionPlan.objects.all()
    for plan in plans:
        features = plan.features
        if 'max_companies' in features:
            del features['max_companies']
        
        # Set max_products based on plan name
        if plan.name.lower() == 'free':
            features['max_products'] = 50
        elif plan.name.lower() == 'standard':
            features['max_products'] = 500
        elif plan.name.lower() == 'premium':
            features['max_products'] = 5000
        
        plan.features = features
        plan.save()

def reverse_update_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('companies', 'SubscriptionPlan')
    
    # Revert changes if needed
    plans = SubscriptionPlan.objects.all()
    for plan in plans:
        features = plan.features
        if 'max_products' in features:
            del features['max_products']
        features['max_companies'] = 1  # Default to 1 company
        plan.features = features
        plan.save()

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_subscription_plans, reverse_update_subscription_plans),
    ] 