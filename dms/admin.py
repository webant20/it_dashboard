from django import forms
from django.contrib import admin
from .models import Document, DocumentLink, PR, PO, Asset, Contract


class DocumentLinkForm(forms.ModelForm):
    object_type = forms.ChoiceField(
        choices=[('PR', 'PR'), ('PO', 'PO'), ('Asset', 'Asset'), ('Contract', 'Contract')],
        widget=forms.Select(attrs={'class': 'object-type-select'})
    )
    object_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'object-id-input'}))

    class Meta:
        model = DocumentLink
        fields = ['object_type', 'object_id']


class DocumentLinkInline(admin.TabularInline):
    model = DocumentLink
    form = DocumentLinkForm
    extra = 1

    def save_model(self, request, obj, form, change):
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.object_type == 'PR' and not PR.objects.filter(pr_number=self.object_id).exists():
            raise ValidationError("Invalid PR number")

        if self.object_type == 'PO' and not PO.objects.filter(po_number=self.object_id).exists():
            raise ValidationError("Invalid PO number")

        if self.object_type == 'Asset':
            try:
                object_id_int = int(self.object_id)  # Convert object_id to integer for Asset ID
            except ValueError:
                raise ValidationError("Invalid Asset ID format")
            if not Asset.objects.filter(asset_id=object_id_int).exists():
                raise ValidationError("Invalid Asset ID")

        if self.object_type == 'Contract' and not Contract.objects.filter(contract_number=self.object_id).exists():
            raise ValidationError("Invalid Contract number")



class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'description', 'uploaded_by', 'uploaded_at')
    inlines = [DocumentLinkInline]

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Document, DocumentAdmin)
