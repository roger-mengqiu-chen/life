# Generated by Django 5.1.4 on 2025-02-09 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_eventtype_unique_event_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactioncategory',
            name='color',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
