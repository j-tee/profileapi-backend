from django.db import models
from django.core.validators import URLValidator
import uuid


class Certification(models.Model):
    """
    Professional certifications
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    name = models.CharField(max_length=200, help_text="Certification name")
    issuer = models.CharField(max_length=200, help_text="Issuing organization")
    issue_date = models.DateField()
    expiration_date = models.DateField(
        blank=True,
        null=True,
        help_text="Leave blank if certification doesn't expire"
    )
    credential_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Certification ID or credential number"
    )
    credential_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="URL to verify certification"
    )
    description = models.TextField(blank=True, null=True)
    skills = models.JSONField(
        default=list,
        help_text="Skills demonstrated by this certification"
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date', 'order']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'
    
    def __str__(self):
        return f"{self.name} - {self.issuer}"
    
    @property
    def is_active(self):
        """Check if certification is still valid"""
        if not self.expiration_date:
            return True
        from django.utils import timezone
        return self.expiration_date > timezone.now().date()
