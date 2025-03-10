# Generated by Django 5.1.4 on 2025-02-10 05:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_history_investment_sum'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_expense', models.FloatField(blank=True, default=0)),
                ('total_income', models.FloatField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ReportLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, default=0)),
                ('percentage', models.FloatField(blank=True, default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.transactioncategory')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.report')),
            ],
        ),
    ]
