# Generated by Django 5.1.6 on 2025-04-06 09:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('AssetApp', '0026_remove_contractnotification_contract_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMTPSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smtp_server', models.CharField(max_length=255)),
                ('smtp_port', models.IntegerField()),
                ('smtp_sender_email', models.CharField(max_length=255)),
                ('smtp_username', models.CharField(blank=True, max_length=255, null=True)),
                ('smtp_password', models.CharField(blank=True, max_length=255, null=True)),
                ('use_tls', models.BooleanField(default=True)),
                ('use_ssl', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ContractNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_ids', models.TextField(help_text='Comma-separated email addresses')),
                ('days_before_expiry', models.TextField(help_text='Comma-separated days before expiry')),
                ('enabled', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='yes', help_text='Enable or disable notifications', max_length=3)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AssetApp.contract')),
            ],
        ),
    ]
