import logging
import pandas as pd
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django_select2.forms import Select2Widget
from django.utils.safestring import mark_safe
from .models import PR, PO, Asset, AssetType, AssetIssue

logger = logging.getLogger(__name__)

# PR Admin Form
class PRAdminForm(forms.ModelForm):
    class Meta:
        model = PR
        fields = ['pr_number', 'description', 'create_date', 'status', 'attachment']

class PRAdmin(admin.ModelAdmin):
    form = PRAdminForm
    list_display = ('pr_number', 'description', 'create_date', 'status')

    def parse_button(self, obj):
        return mark_safe(
        '''
        <!-- JavaScript for PR Parsing -->
        <button type="button" id="parse-pr-button">Parse PR File</button>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const button = document.getElementById("parse-pr-button");
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
                            // Extract PR Number
                            const prNumberMatch = pdfText.match(/Document No:\s+(\d+)/);
                            if (prNumberMatch) {
                                document.querySelector("#id_pr_number").value = prNumberMatch[1];
                                console.log("PR Number found:", prNumberMatch[1]);
                            } else {
                                alert("No PR Number found.");
                            }

                            // Extract PR Date
                            const prDateMatch = pdfText.match(/Date:\s+([\d.]+)/);
                            if (prDateMatch) {
                                const formattedDate = prDateMatch[1].split(".").reverse().join("-");
                                document.querySelector("#id_create_date").value = formattedDate;
                                console.log("PR Date found:", formattedDate);
                            } else {
                                alert("No PR Date found.");
                            }

                            // Extract PR Descriptions using regex
                            const descriptionRegex = /\d{5}\s+\d+\s*([\s\S]+?)\s+\d{2}\.\d{2}\.\d{4}/g;
                            const descriptions = [];
                            let match;
                            while ((match = descriptionRegex.exec(pdfText)) !== null) {
                                descriptions.push(match[1].trim());
                            }
                            if (descriptions.length > 0) {
                                document.querySelector("#id_description").value = descriptions.join(", ");
                                console.log("PR Descriptions found:", descriptions.join(", "));
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
        '''
        )

    parse_button.short_description = "Parse PR File"
    readonly_fields = ["parse_button"]

# PO Admin Form
class POAdminForm(forms.ModelForm):
    class Meta:
        model = PO
        fields = ['po_number', 'pr_number', 'create_date', 'status', 'attachment']

    pr_number = forms.ModelChoiceField(
        queryset=PR.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2', 'style': 'width: 100%;'}),
        required=False,
        label="PR Number",
        help_text="Type or select a PR Number"
    )

class POAdmin(admin.ModelAdmin):
    form = POAdminForm

    list_display = ('po_number', 'pr_number', 'create_date', 'status')

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

import pandas as pd
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from .models import Asset, AssetType, PO

class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'serial_number', 'asset_type', 'po_number')
    change_list_template = "AssetApp/asset_changelist.html"  # To include the "Bulk Upload" button

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
                # Read the uploaded Excel file into a pandas DataFrame
                data = pd.read_excel(file)

                # Iterate over each row in the DataFrame
                for _, row in data.iterrows():
                    try:
                        # Validate Foreign Keys
                        asset_type = AssetType.objects.get(name=row['asset_type'])
                        po_number = PO.objects.get(po_number=row['po_number'])

                        # Create or update the Asset object
                        asset, created = Asset.objects.update_or_create(
                            serial_number=row['serial_number'],
                            defaults={
                                #"asset_type": asset_type,
                                #"po_number": po_number,
                                "sap_asset_id": row['sap_asset_id'],
                                "installation_date": row['installation_date'],
                                "warranty_start_date": row['warranty_start_date'],
                                "warranty_end_date": row['warranty_end_date'],
                                "warranty_provider": row['warranty_provider'],
                                "amc_start_date": row.get('amc_start_date'),
                                "amc_end_date": row.get('amc_end_date'),
                                "amc_provider": row.get('amc_provider'),
                            },
                        )
                        action = "created" if created else "updated"
                        messages.success(request, f"Asset {asset.serial_number} {action} successfully.")

                    except AssetType.DoesNotExist:
                        messages.error(request, f"Asset Type '{row['asset_type']}' not found.")
                    except PO.DoesNotExist:
                        messages.error(request, f"PO Number '{row['po_number']}' not found.")
                    except KeyError as e:
                        messages.error(request, f"Missing column in Excel file: {e}")
                    except Exception as e:
                        messages.error(request, f"Error processing asset {row.get('serial_number', 'unknown')}: {e}")

                return redirect("..")

            except Exception as e:
                messages.error(request, f"Error reading file: {e}")
                return redirect("..")

        # If GET request, render the bulk upload form
        return render(request, "AssetApp/bulk_upload.html", {"title": "Bulk Upload Assets"})

admin.site.register(Asset, AssetAdmin)

admin.site.register(PR, PRAdmin)
admin.site.register(PO, POAdmin)
admin.site.register(AssetType)
admin.site.register(AssetIssue)

