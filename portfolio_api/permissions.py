from rest_framework import permissions
from accounts.models import UserRole


class IsSuperAdmin(permissions.BasePermission):
    """Permission class for super admin only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_super_admin()
        )


class IsEditorOrAbove(permissions.BasePermission):
    """Permission class for editors and super admins"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_edit()
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission class for object owner or admin"""
    
    def has_object_permission(self, request, view, obj):
        # Admins can access anything
        if request.user.is_super_admin():
            return True
        
        # Check if object has 'user' or 'sender' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        elif hasattr(obj, 'profile'):
            return obj.profile.user == request.user if hasattr(obj.profile, 'user') else False
        
        return False


class ReadOnlyOrAuthenticated(permissions.BasePermission):
    """Allow read for anyone, write for authenticated users"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsVerifiedUser(permissions.BasePermission):
    """Permission for verified users only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsSuperAdminOrEditor(permissions.BasePermission):
    """Permission class for super admins and editors"""
    
    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access only for super admins and editors
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_edit()
        )
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access for super admins and editors
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_edit()
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission class for owner or read-only"""
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'profile') and hasattr(obj.profile, 'user'):
            return obj.profile.user == request.user
        
        return False
