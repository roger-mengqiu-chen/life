# Generated by Django 5.1.4 on 2025-05-04 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_utilitytransaction_cost_per_day_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilitytransaction',
            name='month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='utilitytransaction',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
