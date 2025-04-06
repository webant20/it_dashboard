from django.db import models
from AssetApp.models import Contract  # Assuming Contract model is defined in AssetApp.models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
#     description = models.TextField()
#     create_date = models.DateField()

# Create your models here.

# SMTP Settings
class SMTPSettings(models.Model):
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.IntegerField()
    smtp_sender_email = models.CharField(max_length=255)  # Sender email
    smtp_username = models.CharField(max_length=255, blank=True, null=True)  # Username (optional)
    smtp_password = models.CharField(max_length=255, blank=True, null=True)  # Password (optional)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    def __str__(self):
        return f"SMTP Settings ({self.smtp_server})"

class ContractNotification(models.Model):
    ENABLED_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    email_ids = models.TextField(help_text="Comma-separated email addresses")  # Keeping as a string
    days_before_expiry = models.TextField(help_text="Comma-separated days before expiry")  # Storing as a string
    enabled = models.CharField(max_length=3, choices=ENABLED_CHOICES, default='yes', help_text="Enable or disable notifications")

    def get_email_list(self):
        """Convert comma-separated string to a list of valid email addresses."""
        return [email.strip() for email in self.email_ids.split(',') if email.strip()]

    def get_days_list(self):
        """Convert comma-separated days_before_expiry into a list of integers."""
        return [int(day.strip()) for day in self.days_before_expiry.split(',') if day.strip().isdigit()]

    def __str__(self):
        return f"Notification for {self.contract.contract_number if self.contract else 'Unknown Contract'} ({self.enabled})"



class NotificationLog(models.Model):
    email = models.EmailField()
    notification_type = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ('email', 'notification_type', 'sent_at__date')

    def __str__(self):
        return f"{self.notification_type} -> {self.email} @ {self.sent_at}"