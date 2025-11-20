from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_verified', 'mfa_enabled', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'mfa_enabled', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('MFA', {'fields': ('mfa_enabled', 'mfa_secret', 'backup_codes'), 'classes': ('collapse',)}),
        ('Tracking', {'fields': ('last_login', 'last_login_ip', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role')}),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__email', 'action', 'ip_address']
    ordering = ['-timestamp']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'timestamp']
    
    def has_add_permission(self, request):
        return False
