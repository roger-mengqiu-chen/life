# Generated by Django 5.1.4 on 2025-05-04 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_utilitytype_utilitytransaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='utilitytransaction',
            name='transaction_type',
        ),
    ]
