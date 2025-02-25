from django.contrib import admin
from .models import PeriodicActivityMaster, AdHocActivityMaster, PlannedActivity  # Updated import

@admin.register(PeriodicActivityMaster)
class PeriodicActivityMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract', 'frequency', 'start_date', 'end_date', 'status')
    list_filter = ('frequency', 'status', 'contract')
    search_fields = ('name', 'contract__contract_number')

@admin.register(AdHocActivityMaster)  # Updated model name
class AdHocActivityMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract', 'date', 'status')
    list_filter = ('status', 'date', 'contract')
    search_fields = ('name', 'contract__contract_number')

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
