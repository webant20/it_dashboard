# Generated by Django 5.1.4 on 2025-02-16 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AssetApp', '0002_alter_asset_installation_date_alter_asset_po_number_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='asset',
            constraint=models.UniqueConstraint(fields=('asset_type', 'serial_number'), name='unique_asset_type_serial_number'),
        ),
    ]
