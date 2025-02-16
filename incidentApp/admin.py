from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Incident, Category, Attachment
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Customize the admin site titles
admin.site.site_header = "OIL Corporate IT Admin Panel"
admin.site.site_title = "OIL Corporate IT Portal"
admin.site.index_title = "Welcome to the Corporate IT Admin"


# Define a method to display groups
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'is_staff', 'get_groups')

    # Add a method to display groups
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'


        

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1  # Number of empty attachment forms displayed by default
    fields = ('file_path', 'uploaded_by', 'uploaded_at')  # Fields to display in the inline form
    readonly_fields = ('uploaded_at',)  # Make uploaded_at readonly

    def get_readonly_fields(self, request, obj=None):
        """
        Make all attachment fields readonly if the parent incident is closed.
        """
        if obj and obj.status == 'Closed' and not request.user.is_superuser:
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        """
        Disallow adding new attachments if the parent incident is closed.
        """
        if obj and obj.status == 'Closed' and not request.user.is_superuser:
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Disallow deleting attachments if the parent incident is closed.
        """
        if obj and obj.status == 'Closed' and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'reported_by', 'created_at', 'status')
    readonly_fields = ('created_by',)
    inlines = [AttachmentInline]  # Add the inline attachments form

    def save_model(self, request, obj, form, change):
        """
        Automatically set `created_by` and `reported_by` when saving the object.
        Restrict status changes to `Closed` based on permissions.
        """
        print(f"User: {request.user.username}")
        print(f"Permissions: {request.user.get_all_permissions()}")
        print(f"Has `can_close_incident`: {request.user.has_perm('incidentApp.can_close_incident')}")

        if not change:  # If the object is being created
            obj.created_by = request.user
            obj.reported_by = request.user  # Default to the user creating the incident

        if obj.status == 'Closed' and not request.user.has_perm('incidentApp.can_close_incident'):
            raise PermissionDenied("You do not have permission to close incidents.")

        if obj.pk and obj.status == 'Closed' and not request.user.is_superuser:
             if not request.user.has_perm('incidentApp.can_close_incident'):
                raise PermissionDenied("Only administrators or authorized users can close incidents.")

        obj.save()

    def get_queryset(self, request):
        """
        Restrict regular users to only view their own incidents. 
        Superusers can view all incidents.
        """
        qs = super().get_queryset(request)
         # Check if the user is a superuser
        if request.user.is_superuser:
            return qs
    
        # Check if the user belongs to the 'IncidentApp_Admin' group
        if request.user.groups.filter(name='IncidentApp_Admin').exists():
            return qs
    
        # Restrict regular users to only view their own incidents
        return qs.filter(created_by=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Allow users to change their own incidents. Superusers can edit all.
        """
        if obj and not request.user.is_superuser and obj.created_by != request.user and obj.status == 'Closed' and not request.user.groups.filter(name='IncidentApp_Admin').exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Allow users to delete their own incidents. Superusers can delete all.
        """
        if obj and not request.user.is_superuser and obj.created_by != request.user and obj.status == 'Closed'  and not request.user.groups.filter(name='IncidentApp_Admin').exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Make `status` readonly for non-superusers if the incident is closed.
        """
        if obj and obj.status == 'Closed' and not request.user.is_superuser and not request.user.groups.filter(name='IncidentApp_Admin').exists():
#            return self.readonly_fields + ['status']
             return [field.name for field in self.model._meta.fields]  # Make all fields readonly
        return self.readonly_fields

admin.site.register(Incident, IncidentAdmin)
admin.site.register(Category)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

