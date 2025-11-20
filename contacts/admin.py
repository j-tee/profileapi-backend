from django.contrib import admin
from .models import ContactMessage, MessageReply, MessageStatus


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'subject', 'message_type', 'status', 'priority', 'created_at']
    list_filter = ['status', 'message_type', 'priority', 'created_at']
    search_fields = ['sender__email', 'subject', 'message']
    ordering = ['-created_at']
    readonly_fields = ['sender', 'ip_address', 'user_agent', 'created_at', 'updated_at', 'responded_at']
    
    fieldsets = (
        ('Message Info', {'fields': ('sender', 'message_type', 'subject', 'message')}),
        ('Project Details', {'fields': ('project_budget', 'project_timeline', 'attachments'), 'classes': ('collapse',)}),
        ('Status', {'fields': ('status', 'priority', 'admin_notes')}),
        ('Response', {'fields': ('responded_by', 'responded_at'), 'classes': ('collapse',)}),
        ('Metadata', {'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(MessageReply)
class MessageReplyAdmin(admin.ModelAdmin):
    list_display = ['message', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['message__subject', 'author__email', 'content']
    ordering = ['-created_at']
    readonly_fields = ['message', 'author', 'created_at', 'updated_at']
