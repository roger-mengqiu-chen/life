# Generated by Django 5.1.4 on 2025-02-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_accounthistory_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounthistory',
            name='account_amount',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
