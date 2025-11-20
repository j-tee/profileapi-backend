from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
import uuid
import pyotp


class UserRole(models.TextChoices):
    """User role choices for permission management"""
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    EDITOR = 'editor', 'Editor'
    VIEWER = 'viewer', 'Viewer'


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model with email authentication and MFA support
    """
    username = None  # Remove username field
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    
    # Profile information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    
    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
        help_text="User role for permission management"
    )
    
    # Account status
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Account active status"
    )
    
    # MFA fields
    mfa_enabled = models.BooleanField(
        default=False,
        help_text="Multi-factor authentication enabled"
    )
    mfa_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="TOTP secret key for MFA"
    )
    backup_codes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of backup codes for MFA recovery"
    )
    
    # Tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_mfa_secret(self):
        """Generate a new TOTP secret for MFA"""
        if not self.mfa_secret:
            self.mfa_secret = pyotp.random_base32()
            self.save(update_fields=['mfa_secret'])
        return self.mfa_secret
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation"""
        if not self.mfa_secret:
            self.generate_mfa_secret()
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email,
            issuer_name='Portfolio App'
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.mfa_secret:
            return False
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    def verify_backup_code(self, code):
        """Verify and consume backup code"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save(update_fields=['backup_codes'])
            return True
        return False
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes for MFA recovery"""
        import secrets
        self.backup_codes = [
            f"{secrets.token_hex(4)}-{secrets.token_hex(4)}"
            for _ in range(count)
        ]
        self.save(update_fields=['backup_codes'])
        return self.backup_codes
    
    def has_permission(self, permission_level):
        """Check if user has required permission level"""
        permission_hierarchy = {
            UserRole.SUPER_ADMIN: 3,
            UserRole.EDITOR: 2,
            UserRole.VIEWER: 1,
        }
        user_level = permission_hierarchy.get(self.role, 0)
        required_level = permission_hierarchy.get(permission_level, 0)
        return user_level >= required_level
    
    def can_edit(self):
        """Check if user can edit content"""
        return self.has_permission(UserRole.EDITOR)
    
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == UserRole.SUPER_ADMIN or self.is_superuser


class UserActivity(models.Model):
    """Track user activities for security and auditing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=100, help_text="Action performed")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
