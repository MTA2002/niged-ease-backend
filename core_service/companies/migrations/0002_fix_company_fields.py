from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'companies'},
        ),
        migrations.AlterModelOptions(
            name='subscriptionplan',
            options={'ordering': ['price']},
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='company',
            name='subscription_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies', to='companies.subscriptionplan'),
        ),
    ] 