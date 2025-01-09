# Generated by Django 5.0.6 on 2024-07-11 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0005_categorytable_feedetail_category_feedetail_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='membership_type',
        ),
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='phone_no',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
