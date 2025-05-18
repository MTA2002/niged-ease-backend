from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0002_fix_company_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.CharField(default='', max_length=255),
        ),
    ] 