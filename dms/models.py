from django.db import models
from django.contrib.auth.models import User
from AssetApp.models import PR, PO, Contract, Asset
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


# Document Management System Models
class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='documents/', max_length=100)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
# Signal to delete the actual file from media/documents when document is deleted
@receiver(post_delete, sender=Document)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class DocumentLink(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('PR', 'PR'),
        ('PO', 'PO'),
        ('Asset', 'Asset'),
        ('Contract', 'Contract')
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)
    object_id = models.CharField(max_length=100)

    class Meta:
        unique_together = ('document', 'object_type', 'object_id')

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.object_type == 'PR' and not PR.objects.filter(pr_number=self.object_id).exists():
            raise ValidationError("Invalid PR number")

        if self.object_type == 'PO' and not PO.objects.filter(po_number=self.object_id).exists():
            raise ValidationError("Invalid PO number")

        if self.object_type == 'Asset' and not Asset.objects.filter(asset_id=self.object_id).exists():
            raise ValidationError("Invalid Asset ID")

        if self.object_type == 'Contract' and not Contract.objects.filter(contract_number=self.object_id).exists():
            raise ValidationError("Invalid Contract number")
