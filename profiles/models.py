from django.db import models
from django.core.validators import URLValidator
from django.conf import settings
import uuid


class Profile(models.Model):
    """
    Portfolio profile for the site owner only.
    Contains professional information, bio, and portfolio details.
    This is NOT auto-created - should be manually created for the site owner.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_profile',
        help_text="The user who owns this portfolio profile"
    )
    
    # Professional information
    headline = models.CharField(
        max_length=255,
        help_text="Professional headline or tagline"
    )
    summary = models.TextField(
        help_text="Professional summary or bio"
    )
    
    # Location (optional)
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
        verbose_name = 'Portfolio Profile'
        verbose_name_plural = 'Portfolio Profiles'
    
    def __str__(self):
        return f"{self.user.full_name}'s Portfolio"


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
