# Generated by Django 5.1.4 on 2025-01-23 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_transaction_transaction_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transactioncategory',
            options={'verbose_name_plural': 'Transaction Categories'},
        ),
    ]
