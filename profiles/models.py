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
    
    @property
    def is_complete(self):
        """Check if profile has all required information filled out"""
        return bool(
            self.city and 
            self.state and 
            self.country and 
            self.headline and 
            len(self.summary) > 50  # At least 50 chars in summary
        )


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
