from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Incident, Category, Attachment, Comment
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Customize the admin site titles
admin.site.site_header = "OIL Corporate IT Admin Panel"
admin.site.site_title = "OIL Corporate IT Portal"
admin.site.index_title = "Welcome to the Corporate IT Admin"

# Define a method to display groups
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

# Inline for Attachments linked to Incidents
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1
    fields = ('file_path', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

    def has_add_permission(self, request, obj=None):
        return not (obj and obj.status == 'Closed' and not request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.status == 'Closed' and not request.user.is_superuser)

# Inline for Attachments linked to Comments
class CommentAttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1
    fields = ('file_path', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

    def has_add_permission(self, request, obj=None):
        return obj and obj.incident.status != 'Closed' or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return obj and obj.incident.status != 'Closed' or request.user.is_superuser

# Comment Inline inside IncidentAdmin
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('comment', 'commented_by', 'created_at')
    readonly_fields = ('created_at', 'commented_by')

    def save_model(self, request, obj, form, change):
        if not obj.commented_by:
            obj.commented_by = request.user
        obj.save()

# Comment Admin with Attachments
class CommentAdmin(admin.ModelAdmin):
    list_display = ('incident', 'commented_by', 'created_at')
    search_fields = ('comment', 'incident__title', 'commented_by__username')
    list_filter = ('created_at',)
    inlines = [CommentAttachmentInline]  # Attachments for comments

    def save_model(self, request, obj, form, change):
        if not obj.commented_by:
            obj.commented_by = request.user
        obj.save()

# Incident Admin
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'reported_by', 'created_at', 'status')
    readonly_fields = ('created_by',)
    inlines = [AttachmentInline, CommentInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.reported_by = request.user
        if obj.status == 'Closed' and not request.user.has_perm('incidentApp.can_close_incident'):
            raise PermissionDenied("You do not have permission to close incidents.")
        obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='IncidentApp_Admin').exists():
            return qs
        return qs.filter(created_by=request.user)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'Closed' and not request.user.is_superuser and not request.user.groups.filter(name='IncidentApp_Admin').exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'Closed' and not request.user.is_superuser and not request.user.groups.filter(name='IncidentApp_Admin').exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'Closed' and not request.user.is_superuser and not request.user.groups.filter(name='IncidentApp_Admin').exists():
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

admin.site.register(Incident, IncidentAdmin)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
