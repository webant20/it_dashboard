# Generated by Django 5.1.6 on 2025-02-26 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AssetApp', '0010_asset_end_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='amc_end_date',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='amc_provider',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='amc_start_date',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='warranty_end_date',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='warranty_provider',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='warranty_start_date',
        ),
        migrations.AddField(
            model_name='asset',
            name='amc_contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets_under_amc', to='AssetApp.contract'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial_number',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
