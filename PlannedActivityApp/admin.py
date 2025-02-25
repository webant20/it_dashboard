from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from .models import PeriodicActivityMaster, AdHocActivityMaster, PlannedActivity
from django.contrib.auth.models import User
from datetime import timedelta


# Function to generate planned activities
def generate_planned_activities():
    FREQUENCY_MAPPING = {
        "Weekly": 7,
        "Monthly": 30,  # Approximate
        "Quarterly": 90,
        "Half-Yearly": 180,
        "Yearly": 365,
    }

    today = now().date()
    
    for activity in PeriodicActivityMaster.objects.filter(status="Enabled"):
        frequency_days = FREQUENCY_MAPPING.get(activity.frequency)

        if not frequency_days:
            continue

        due_date = activity.start_date
        while due_date <= activity.end_date:
            if due_date >= today:
                if not PlannedActivity.objects.filter(periodic_activity=activity, due_date=due_date).exists():
                    assigned_user = User.objects.order_by('?').first()  # Assign randomly
                    PlannedActivity.objects.create(
                        periodic_activity=activity,
                        due_date=due_date,
                        assigned_to=None,
                        status="Open"
                    )

            due_date += timedelta(days=frequency_days)


# Admin action to trigger activity generation
def generate_planned_activity_action(modeladmin, request, queryset):
    generate_planned_activities()
    messages.success(request, "Planned activities have been generated successfully!")
    return HttpResponseRedirect(request.get_full_path())

generate_planned_activity_action.short_description = "Generate Planned Activities"


# Admin for PeriodicActivityMaster with a button
@admin.register(PeriodicActivityMaster)
class PeriodicActivityMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract', 'frequency', 'start_date', 'end_date', 'status', 'generate_button')
    list_filter = ('frequency', 'status', 'contract')
    search_fields = ('name', 'contract__contract_number')
    actions = [generate_planned_activity_action]  # Add action

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-planned-activities/', self.admin_site.admin_view(self.generate_planned_activities_view), name="generate_planned_activities"),
        ]
        return custom_urls + urls

    def generate_planned_activities_view(self, request):
        generate_planned_activities()
        self.message_user(request, "Planned activities have been generated successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    def generate_button(self, obj):
        return format_html('<a class="button" href="{}">Generate</a>', "/admin/PlannedActivityApp/periodicactivitymaster/generate-planned-activities/")
    
    generate_button.allow_tags = True
    generate_button.short_description = "Generate Planned Activities"


# Admin for AdHocActivityMaster with the same button
@admin.register(AdHocActivityMaster)
class AdHocActivityMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract', 'date', 'status', 'generate_button')
    list_filter = ('status', 'date', 'contract')
    search_fields = ('name', 'contract__contract_number')
    actions = [generate_planned_activity_action]  # Add action

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-planned-activities/', self.admin_site.admin_view(self.generate_planned_activities_view), name="generate_planned_activities"),
        ]
        return custom_urls + urls

    def generate_planned_activities_view(self, request):
        generate_planned_activities()
        self.message_user(request, "Planned activities have been generated successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    def generate_button(self, obj):
        return format_html('<a class="button" href="{}">Generate</a>', "/admin/PlannedActivityApp/adhocactivitymaster/generate-planned-activities/")
    
    generate_button.allow_tags = True
    generate_button.short_description = "Generate Planned Activities"


@admin.register(PlannedActivity)
class PlannedActivityAdmin(admin.ModelAdmin):
    list_display = ("periodic_activity", "due_date", "assigned_to", "status")
    list_filter = ("status", "due_date")
    search_fields = ("periodic_activity__name", "assigned_to__username")

    def get_queryset(self, request):
        """Restrict non-superusers to only see their assigned activities."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers see all records
        return qs.filter(assigned_to=request.user)  # Non-superusers see only their assigned records

    def get_form(self, request, obj=None, **kwargs):
        """Restrict 'assigned_to' field visibility for non-superusers."""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields["assigned_to"].disabled = True
        return form
