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
