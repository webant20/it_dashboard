# Generated by Django 5.1.6 on 2025-02-26 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AssetApp', '0008_remove_enduser_location_status_enduser_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enduser',
            name='location',
            field=models.TextField(default='OILHOUSE'),
        ),
        migrations.AlterField(
            model_name='enduser',
            name='name',
            field=models.CharField(default='IT', max_length=255, unique=True),
        ),
    ]
