from django.db import models
from AssetApp.models import Contract
class PeriodicActivityMaster(models.Model):
    class Frequency(models.TextChoices):
        WEEKLY = 'Weekly', 'Weekly'
        MONTHLY = 'Monthly', 'Monthly'
        QUARTERLY = 'Quarterly', 'Quarterly'
        HALF_YEARLY = 'Half-Yearly', 'Half-Yearly'
        YEARLY = 'Yearly', 'Yearly'

    class Status(models.TextChoices):
        ENABLED = 'Enabled', 'Enabled'
        DISABLED = 'Disabled', 'Disabled'

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ENABLED)

    def __str__(self):
        return f"{self.name} - {self.frequency}"


class AdHocActivityMaster(models.Model):  # Renamed model
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    date = models.DateField()

    class Status(models.TextChoices):
        ENABLED = 'Enabled', 'Enabled'
        DISABLED = 'Disabled', 'Disabled'

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ENABLED
    )

    def __str__(self):
        return f"{self.name} - {self.contract.contract_number}"

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class PlannedActivity(models.Model):
    class Status(models.TextChoices):
        OPEN = 'Open', 'Open'
        CLOSED = 'Closed', 'Closed'

    periodic_activity = models.ForeignKey("PeriodicActivityMaster", on_delete=models.CASCADE)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    activity_completion_documents = models.FileField(upload_to='planned_activity_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.periodic_activity.name} - {self.due_date}"
