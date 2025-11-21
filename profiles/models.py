from django.db import models
from django.core.validators import URLValidator
import uuid


class Profile(models.Model):
    """
    Main profile model representing the user's professional profile
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    headline = models.CharField(max_length=255, help_text="Professional headline or tagline")
    summary = models.TextField(help_text="Professional summary or bio")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    
    # Images
    profile_picture = models.ImageField(
        upload_to='profiles/pictures/',
        blank=True,
        null=True
    )
    cover_image = models.ImageField(
        upload_to='profiles/covers/',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    SUMMARY_MIN_LENGTH = 50
    REQUIRED_FIELDS = ['headline', 'summary', 'city', 'state', 'country']
    
    @property
    def is_complete(self):
        """Profile is complete only when no required fields are missing"""
        return not self.missing_required_fields()
    
    def missing_required_fields(self):
        """Return list of required fields that still need user input"""
        missing = []
        if not self.headline:
            missing.append('headline')
        if not self.summary or len(self.summary.strip()) < self.SUMMARY_MIN_LENGTH:
            missing.append('summary')
        if not self.city:
            missing.append('city')
        if not self.state:
            missing.append('state')
        if not self.country:
            missing.append('country')
        return missing
    
    def completion_status(self):
        """Convenient structure for API responses"""
        missing = self.missing_required_fields()
        return {
            'is_complete': not missing,
            'needs_update': bool(missing),
            'missing_fields': missing,
            'summary_min_length': self.SUMMARY_MIN_LENGTH
        }


class SocialLink(models.Model):
    """
    Social media and portfolio links
    """
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='social_links'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField(validators=[URLValidator()])
    display_name = models.CharField(max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'platform']
        unique_together = ['profile', 'platform', 'url']
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.get_platform_display()}"
