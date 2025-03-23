import logging
import pandas as pd
import numpy as np
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django_select2.forms import Select2Widget
from django.utils.safestring import mark_safe
from .models import PR, PO, Asset, Location,AssetType, AssetIssue, Contract, ContractNotification, SMTPSettings,EndUser
from dms.models import Document, DocumentLink


logger = logging.getLogger(__name__)
class PRAdminForm(forms.ModelForm):
    # file_upload = forms.FileField(
    #     widget=forms.FileInput(),
    #     required=False,
    #     label="Upload File for Parsing"
    # )

    class Meta:
        model = PR
        fields = '__all__'


class PRAdmin(admin.ModelAdmin):
    form = PRAdminForm
    list_display = ('pr_number', 'description', 'create_date', 'status')
    search_fields = ['pr_number', 'description', 'create_date', 'status']
    list_filter = ['status']

    readonly_fields = ["parse_button", "linked_documents"]

    def parse_button(self, obj):
        return mark_safe(
        '''
        <!-- JavaScript for PR Parsing -->
        <input type="file" id="pr-attachment" />
        <button type="button" id="parse-pr-button">Parse PR File</button>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const button = document.getElementById("parse-pr-button");
            button.addEventListener("click", function() {
                const attachmentInput = document.querySelector("#pr-attachment");
                if (!attachmentInput || !attachmentInput.files.length) {
                    alert("Please upload a file before parsing.");
                    return;
                }

                const file = attachmentInput.files[0];
                const reader = new FileReader();
                reader.onload = function(e) {
                    const typedArray = new Uint8Array(e.target.result);
                    const pdfjsLib = window['pdfjs-dist/build/pdf'];
                    pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";

                    pdfjsLib.getDocument(typedArray).promise.then(function(pdf) {
                        let pdfText = "";
                        const pagePromises = [];
                        for (let i = 1; i <= pdf.numPages; i++) {
                            pagePromises.push(
                                pdf.getPage(i).then(function(page) {
                                    return page.getTextContent().then(function(textContent) {
                                        textContent.items.forEach(item => {
                                            pdfText += item.str + " ";
                                        });
                                    });
                                })
                            );
                        }

                        Promise.all(pagePromises).then(() => {
                            const prNumberMatch = pdfText.match(/Document No:\s+(\d+)/);
                            if (prNumberMatch) {
                                document.querySelector("#id_pr_number").value = prNumberMatch[1];
                            } else {
                                alert("No PR Number found.");
                            }

                            const prDateMatch = pdfText.match(/Date:\s+([\d.]+)/);
                            if (prDateMatch) {
                                const formattedDate = prDateMatch[1].split(".").reverse().join("-");
                                document.querySelector("#id_create_date").value = formattedDate;
                            } else {
                                alert("No PR Date found.");
                            }

                            const descriptionRegex = /\d{5}\s+\d+\s*([\s\S]+?)\s+\d{2}\.\d{2}\.\d{4}/g;
                            const descriptions = [];
                            let match;
                            while ((match = descriptionRegex.exec(pdfText)) !== null) {
                                descriptions.push(match[1].trim());
                            }
                            if (descriptions.length > 0) {
                                document.querySelector("#id_description").value = descriptions.join(", ");
                            } else {
                                alert("No PR Descriptions found.");
                            }
                        }).catch(console.error);
                    }).catch(console.error);
                };

                reader.readAsArrayBuffer(file);
            });
        });
        </script>
        ''')

    parse_button.short_description = "Parse PR File"

    def linked_documents(self, obj):
        document_links = DocumentLink.objects.filter(object_type='PR', object_id=obj.id)
        files_html = ""
        for link in document_links:
            document = link.document
            files_html += f'<a href="{document.file.url}" target="_blank">{document.file.name}</a><br>'
        
        return format_html(files_html)

    linked_documents.short_description = "Uploaded Attachments"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        attachment = form.cleaned_data.get('attachment')
        if attachment:
            document = Document.objects.create(
                description="PR Attachment",
                file=attachment,
                uploaded_by=request.user
            )

            DocumentLink.objects.create(
                object_type='PR',
                object_id=obj.pr_number,
                document=document
            )


# PO Admin Form
class POAdminForm(forms.ModelForm):
    class Meta:
        model = PO
        fields = ['po_number','description' ,'pr_number', 'create_date', 'status', 'attachment']

    pr_number = forms.ModelChoiceField(
        queryset=PR.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2', 'style': 'width: 100%;'}),
        required=False,
        label="PR Number",
        help_text="Type or select a PR Number"
    )

class POAdmin(admin.ModelAdmin):
    form = POAdminForm

    list_display = ('po_number', 'pr_number', 'create_date', 'status','description')
    

    search_fields = ['po_number', 'pr_number', 'create_date', 'status']
    list_display_links = ('po_number','pr_number',)

    def parse_button(self, obj):
        return mark_safe(
        '''
        <!-- JavaScript for PO Parsing -->
        <button type="button" id="parse-po-button">Parse PO File</button>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const button = document.getElementById("parse-po-button");
            button.addEventListener("click", function() {
                const attachmentInput = document.querySelector("#id_attachment");
                if (!attachmentInput || !attachmentInput.files.length) {
                    alert("Please upload a file before parsing.");
                    return;
                }

                const file = attachmentInput.files[0];
                const reader = new FileReader();
                reader.onload = function(e) {
                    const typedArray = new Uint8Array(e.target.result);
                    const pdfjsLib = window['pdfjs-dist/build/pdf'];
                    pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";

                    pdfjsLib.getDocument(typedArray).promise.then(function(pdf) {
                        let pdfText = "";
                        const pagePromises = [];
                        for (let i = 1; i <= pdf.numPages; i++) {
                            pagePromises.push(
                                pdf.getPage(i).then(function(page) {
                                    return page.getTextContent().then(function(textContent) {
                                        textContent.items.forEach(item => {
                                            pdfText += item.str + " ";
                                        });
                                    });
                                })
                            );
                        }

                        Promise.all(pagePromises).then(() => {
                            const poNumberMatch = pdfText.match(/PURCHASE ORDER NO\s*:\s*([\w\/.-]+)/);
                            if (poNumberMatch) {
                                const poNumber = poNumberMatch[1].trim();
                                document.querySelector("#id_po_number").value = poNumber;
                                console.log("PO Number found:", poNumber);
                            } else {
                                alert("No PO Number found.");
                                console.log("PO Number not found.");
                            }

                            const poDateMatch = pdfText.match(/PURCHASE ORDER DATE\s*:\s*([\d.]+)/);
                            if (poDateMatch) {
                                const formattedDate = poDateMatch[1].split(".").reverse().join("-");
                                document.querySelector("#id_create_date").value = formattedDate;
                                console.log("PO Date found:", formattedDate);
                            } else {
                                alert("No PO Date found.");
                                console.log("PO Date not found.");
                            }
                        }).catch(console.error);
                    }).catch(console.error);
                };

                reader.readAsArrayBuffer(file);
            });
        });
        </script>
        '''
        )

    parse_button.short_description = "Parse PO File"
    readonly_fields = ["parse_button"]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location',)
    search_fields = ('location__icontains',)
    ordering = ('location',)

class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'asset_id', 'sap_asset_id', 'serial_number', 'asset_type', 'asset_description', 
        'installation_date', 'amc_start_date', 'amc_end_date', 'amc_contract_link', 
        'warranty_start_date', 'warranty_end_date', 'po_number_link', 'end_user', 'location'
    )
    search_fields = [
        'serial_number', 'sap_asset_id', 'asset_type__name', 'po_number__po_number', 
        'asset_description', 'end_user__name', 'amc_contract__contract_number', 
        'location__location', 'location__office'  # ✅ Added office field
    ]
    list_filter = ['asset_type', 'po_number', 'end_user', 'amc_contract', 'location']
    list_display_links = ('asset_id',)  # Keeping asset_id as a link
    ordering = [models.F('installation_date').desc(nulls_last=True)]  # Sort by installation_date descending, blank at bottom



    change_list_template = "AssetApp/asset_changelist.html"  # Bulk Upload button

    @admin.display(description="PO Number")
    def po_number_link(self, obj):
        """Generates a clickable link to the PO admin page."""
        if obj.po_number:
            url = reverse('admin:AssetApp_po_change', args=[obj.po_number.id])
            return format_html('<a href="{}">{}</a>', url, obj.po_number.po_number)
        return "-"

    @admin.display(description="AMC Contract")
    def amc_contract_link(self, obj):
        """Generates a clickable link to the Contract admin page."""
        if obj.amc_contract:
            url = reverse('admin:AssetApp_contract_change', args=[obj.amc_contract.contract_number])  # Use contract_number instead of id
            return format_html('<a href="{}">{}</a>', url, obj.amc_contract.contract_number)
        return "-"



    # @admin.display(description="End User Location")
    # def end_user_location(self, obj):
    #     """Fetches location from the associated EndUser model"""
    #     return obj.end_user.location if obj.end_user else "N/A"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.bulk_upload_view, name='asset_bulk_upload'),
        ]
        return custom_urls + urls
        
    def bulk_upload_view(self, request):
        if request.method == "POST" and request.FILES.get("file"):
            file = request.FILES["file"]
            try:
                data = pd.read_excel(file)
                data = data.replace({np.nan: None})  # Replace NaN with None

                for _, row in data.iterrows():
                    try:
                        # Fetching Foreign Key References
                        asset_type = AssetType.objects.get(name=row['asset_type'])
                            
                        # Convert PO number to string and strip '.0' if it exists
                        po_number = str(row['po_number']).rstrip('.0') if row.get('po_number') else None
                        po_number = PO.objects.get(po_number=po_number) if row.get('po_number') else None
                        # po_number = PO.objects.get(po_number=row['po_number']) if row.get('po_number') else None
                        end_user = EndUser.objects.get(name=row['end_user']) if row.get('end_user') else None
                        amc_contract = Contract.objects.get(contract_number=row['amc_contract']) if row.get('amc_contract') else None
                        # office = Location.objects.get(office=row['office']) if row.get('office') else None
                        location = Location.objects.get(location=row['location']) if row.get('location') else None

                        # Handle Dates with Proper Conversion
                        installation_date = pd.to_datetime(row['installation_date']).date() if row.get('installation_date') else None
                        amc_start_date = pd.to_datetime(row['amc_start_date']).date() if row.get('amc_start_date') else None
                        amc_end_date = pd.to_datetime(row['amc_end_date']).date() if row.get('amc_end_date') else None
                        warranty_start_date = pd.to_datetime(row['warranty_start_date']).date() if row.get('warranty_start_date') else None
                        warranty_end_date = pd.to_datetime(row['warranty_end_date']).date() if row.get('warranty_end_date') else None

                        # Create or Update the Asset
                        asset, created = Asset.objects.update_or_create(
                            serial_number=row['serial_number'],
                            defaults={
                                "asset_type": asset_type,
                                "asset_description": row.get('asset_description', ''),
                                "po_number": po_number,
                                "sap_asset_id": row.get('sap_asset_id', ''),
                                "installation_date": installation_date,
                                "location": location,
                                "amc_start_date": amc_start_date,
                                "amc_end_date": amc_end_date,
                                "warranty_start_date": warranty_start_date,
                                "warranty_end_date": warranty_end_date,
                                "amc_contract": amc_contract,
                                "end_user": end_user
                            },
                        )

                        action = "created" if created else "updated"
                        messages.success(request, f"Asset {asset.serial_number} {action} successfully.")

                    except AssetType.DoesNotExist:
                        messages.error(request, f"Asset Type '{row['asset_type']}' not found.")
                    except PO.DoesNotExist:
                        messages.error(request, f"PO Number '{row['po_number']}' not found.")
                    except EndUser.DoesNotExist:
                        messages.error(request, f"End User '{row['end_user']}' not found.")
                    except Contract.DoesNotExist:
                        messages.error(request, f"Contract '{row['amc_contract']}' not found.")
                    except Location.DoesNotExist:
                        messages.error(request, f"Location '{row['location']}' not found.")
                    except KeyError as e:
                        messages.error(request, f"Missing column in Excel file: {e}")
                    except Exception as e:
                        messages.error(request, f"Error processing asset {row.get('serial_number', 'unknown')}: {e}")

                return redirect("..")

            except Exception as e:
                messages.error(request, f"Error reading file: {e}")
                return redirect("..")

        return render(request, "AssetApp/bulk_upload.html", {"title": "Bulk Upload Assets"})

admin.site.register(Asset, AssetAdmin)

admin.site.register(PR, PRAdmin)
admin.site.register(PO, POAdmin)
admin.site.register(AssetType)
admin.site.register(AssetIssue)

from django.contrib import admin
from .models import Contract, ContractNotification, SMTPSettings, ContractAttachment

class ContractAttachmentInline(admin.TabularInline):  # Inline for attachments
    model = ContractAttachment
    extra = 1  # Show one empty attachment field by default
    fields = ('file','description')  # Show only the file upload field

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'description', 'start_date', 'end_date', 'status')
    search_fields = ('contract_number', 'description')
    list_filter = ('status', 'start_date', 'end_date')
    inlines = [ContractAttachmentInline]  # Add inline attachments

@admin.register(ContractAttachment)
class ContractAttachmentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'file', 'uploaded_at')
    search_fields = ('contract__contract_number',)

@admin.register(ContractNotification)
class ContractNotificationAdmin(admin.ModelAdmin):
    list_display = ('contract', 'email_ids', 'days_before_expiry')
    search_fields = ('contract__contract_number', 'email_ids')

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('smtp_server', 'smtp_port', 'smtp_username', 'use_tls', 'use_ssl')
    search_fields = ('smtp_server', 'smtp_username')

@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    search_fields = ('name', )
    list_filter = ('status',)