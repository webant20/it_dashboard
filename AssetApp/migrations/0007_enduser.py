# Generated by Django 5.1.6 on 2025-02-26 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AssetApp', '0006_delete_enduser'),
    ]

    operations = [
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('location_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
            ],
        ),
    ]
