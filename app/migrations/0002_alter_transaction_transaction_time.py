# Generated by Django 5.1.4 on 2025-01-23 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_time',
            field=models.DateField(),
        ),
    ]
