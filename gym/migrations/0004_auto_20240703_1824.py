# Generated by Django 3.2.12 on 2024-07-03 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0003_remove_customer_due_date_remove_customer_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='admission_number',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.DeleteModel(
            name='YearlyFee',
        ),
    ]