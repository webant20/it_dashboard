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
    attachment = models.FileField(upload_to='pr_attachments/')

    def __str__(self):
        return self.pr_number

# PO Model
class PO(models.Model):
    po_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # Allows empty descriptions
    pr_number = models.ForeignKey(PR, on_delete=models.CASCADE,null=True, blank=True)
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

# AssetType Model
class AssetType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Asset Model
class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    asset_description = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100)
    po_number = models.ForeignKey(PO, on_delete=models.CASCADE, null=True, blank=True)
    sap_asset_id = models.CharField(max_length=100, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    warranty_provider = models.CharField(max_length=100, null=True, blank=True)
    amc_start_date = models.DateField(null=True, blank=True)
    amc_end_date = models.DateField(null=True, blank=True)
    amc_provider = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['asset_type', 'serial_number'], name='unique_asset_type_serial_number')
        ]

    def __str__(self):
        return f"Asset {self.asset_id}"


# Asset Issue Model
class AssetIssue(models.Model):
    asset_id = models.ForeignKey(Asset, on_delete=models.CASCADE)
    issued_to = models.CharField(max_length=100)
    issue_date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Issue {self.asset_id.asset_id} to {self.issued_to}"
    
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

class ContractNotification(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    email_ids = models.TextField(help_text="Comma-separated email addresses")
    days_before_expiry = models.PositiveIntegerField(help_text="Days before expiry to trigger notification")

    def get_email_list(self):
        return [email.strip() for email in self.email_ids.split(',')]
    
    def __str__(self):
        return f"Notification for {self.contract.contract_number}"

class SMTPSettings(models.Model):
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.IntegerField()
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    def __str__(self):
        return f"SMTP Settings ({self.smtp_server})"


