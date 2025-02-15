# Generated by Django 5.1.4 on 2025-01-13 05:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('unit_no', models.IntegerField(blank=True, null=True)),
                ('building_no', models.IntegerField(blank=True, null=True)),
                ('street_no', models.CharField(blank=True, max_length=255, null=True)),
                ('street_name', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Location',
            },
        ),
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_income', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('website', models.URLField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.location')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.gender')),
                ('merchant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.merchant')),
            ],
            options={
                'verbose_name_plural': 'People',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_time', models.DateTimeField()),
                ('name', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, null=True)),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.eventtype')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.location')),
                ('people', models.ManyToManyField(to='app.person')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('transaction_time', models.DateTimeField()),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.merchant')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.transactioncategory')),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.transactiontype')),
            ],
        ),
        migrations.AddConstraint(
            model_name='merchant',
            constraint=models.UniqueConstraint(fields=('name', 'location'), name='unique_merchant_name'),
        ),
    ]
