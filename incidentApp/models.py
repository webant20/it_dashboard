from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Incident(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed')
    ]
    title = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.PROTECT,default=1) 
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents_created',null=True,blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents_reported',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

class Attachment(models.Model):
    file_path = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)

class Comment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Audit Log model
class AuditLog(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

# SLA model
class SLA(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sla_rules')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    response_time = models.PositiveIntegerField(help_text='In minutes')
    resolution_time = models.PositiveIntegerField(help_text='In minutes')

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


