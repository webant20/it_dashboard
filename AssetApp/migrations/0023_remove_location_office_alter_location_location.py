# Generated by Django 5.1.6 on 2025-03-23 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AssetApp', '0022_alter_location_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='office',
        ),
        migrations.AlterField(
            model_name='location',
            name='location',
            field=models.CharField(default='IT', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
