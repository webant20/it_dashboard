from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# PR Model
class PR(models.Model):
    pr_number = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    create_date = models.DateField()

    class Status(models.TextChoices):
        OPEN = 'Open', _('Open')
        CLOSED = 'Closed', _('Closed')

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
    )
    # attachment = models.FileField(upload_to='pr_attachments/')

    def __str__(self):
        return self.pr_number


# PO Model
class PO(models.Model):
    po_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # Allows empty descriptions
    pr_number = models.ForeignKey(PR, on_delete=models.CASCADE, null=True, blank=True)
    create_date = models.DateField()

    class Status(models.TextChoices):
        OPEN = 'Open', _('Open')
        CLOSED = 'Closed', _('Closed')

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
    )
    attachment = models.FileField(upload_to='po_attachments/')

    def __str__(self):
        return self.po_number

class POAttachment(models.Model):
    po = models.ForeignKey('PO', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='po_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.file.name}"


# Contract Model
class Contract(models.Model):
    contract_number = models.CharField(max_length=100, primary_key=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    pr_number = models.ForeignKey(PR, on_delete=models.CASCADE, blank=True, null=True)
    wo_number = models.ForeignKey(PO, on_delete=models.CASCADE, blank=True, null=True)

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        EXPIRED = 'Expired', 'Expired'

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.EXPIRED,
        editable=False  # Prevent manual changes
    )

    def save(self, *args, **kwargs):
        current_date = timezone.now().date()
        if self.start_date <= current_date <= self.end_date:
            self.status = self.Status.ACTIVE
        else:
            self.status = self.Status.EXPIRED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.contract_number


# AssetType Model
class AssetType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    location = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.location


# Asset Model
class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    asset_description = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100, unique=True)
    po_number = models.ForeignKey(PO, on_delete=models.CASCADE, null=True, blank=True)
    sap_asset_id = models.CharField(max_length=100, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    amc_start_date = models.DateField(null=True, blank=True)
    amc_end_date = models.DateField(null=True, blank=True)
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)

    # New Field: AMC Contract Reference
    amc_contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets_under_amc")

    end_user = models.ForeignKey('EndUser', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['asset_type', 'serial_number'], name='unique_asset_type_serial_number')
        ]

    def __str__(self):
        return f"Asset {self.asset_id} - {self.asset_type.name} - {self.serial_number}"


# Asset Issue Model
class AssetIssue(models.Model):
    asset_id = models.ForeignKey(Asset, on_delete=models.CASCADE)
    issued_to = models.CharField(max_length=100)
    issue_date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Issue {self.asset_id.asset_id} to {self.issued_to}"


# Contract Attachments
class ContractAttachment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='contracts/')
    description = models.TextField(blank=True, null=True)  # Added description field
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.contract.contract_number} - {self.description[:20] if self.description else 'No Description'}"


# class ContractNotification(models.Model):
#     ENABLED_CHOICES = [
#         ('yes', 'Yes'),
#         ('no', 'No'),
#     ]

#     contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
#     email_ids = models.TextField(help_text="Comma-separated email addresses")  # Keeping as a string
#     days_before_expiry = models.TextField(help_text="Comma-separated days before expiry")  # Storing as a string
#     enabled = models.CharField(max_length=3, choices=ENABLED_CHOICES, default='yes', help_text="Enable or disable notifications")

#     def get_email_list(self):
#         """Convert comma-separated string to a list of valid email addresses."""
#         return [email.strip() for email in self.email_ids.split(',') if email.strip()]

#     def get_days_list(self):
#         """Convert comma-separated days_before_expiry into a list of integers."""
#         return [int(day.strip()) for day in self.days_before_expiry.split(',') if day.strip().isdigit()]

#     def __str__(self):
#         return f"Notification for {self.contract.contract_number if self.contract else 'Unknown Contract'} ({self.enabled})"


# End User Model
class EndUser(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name

