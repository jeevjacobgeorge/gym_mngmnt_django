# Generated by Django 5.0.6 on 2024-07-10 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0004_auto_20240703_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('WT', 'Weight Training'), ('C', 'Cardio'), ('B', 'Both')], default='WT', max_length=2)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='feedetail',
            name='category',
            field=models.CharField(choices=[('WT', 'Weight Training'), ('C', 'Cardio'), ('B', 'Both')], default='WT', max_length=2),
        ),
        migrations.AddField(
            model_name='feedetail',
            name='year',
            field=models.IntegerField(default=2024),
        ),
    ]
