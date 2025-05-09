# Generated by Django 5.1.4 on 2025-05-02 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_investment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='merchant',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='transactioncategory',
            options={'ordering': ['name'], 'verbose_name_plural': 'Transaction Categories'},
        ),
        migrations.AlterField(
            model_name='history',
            name='existing_sum',
            field=models.FloatField(blank=True, default=0, help_text='Existing sum is total - car/house'),
        ),
    ]
