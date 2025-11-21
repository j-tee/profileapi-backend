from django.db import models
from django.core.validators import URLValidator
from django.conf import settings
import uuid


class Project(models.Model):
    """
    Portfolio projects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Short description")
    long_description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed project description"
    )
    technologies = models.JSONField(
        default=list,
        help_text="List of technologies used"
    )
    role = models.CharField(max_length=100, help_text="Your role in the project")
    team_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of team members"
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=False, help_text="Currently working on this")
    
    # URLs
    project_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Live project URL"
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="GitHub repository URL"
    )
    demo_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Demo or video URL"
    )
    
    # Media files
    video = models.FileField(
        upload_to='projects/videos/',
        blank=True,
        null=True,
        help_text="Project demo video"
    )
    
    # Additional details
    highlights = models.JSONField(
        default=list,
        help_text="Key highlights or features"
    )
    challenges = models.TextField(
        blank=True,
        null=True,
        help_text="Challenges faced and solutions"
    )
    outcomes = models.TextField(
        blank=True,
        null=True,
        help_text="Results and impact"
    )
    
    featured = models.BooleanField(
        default=False,
        help_text="Feature this project on profile"
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-start_date', 'order']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    """
    Images for projects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='projects/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"{self.project.title} - Image {self.order}"
