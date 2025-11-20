from django.db import models
import uuid


class Experience(models.Model):
    """
    Professional experience/work history
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    LOCATION_TYPE_CHOICES = [
        ('on_site', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    title = models.CharField(max_length=200, help_text="Job title")
    company = models.CharField(max_length=200)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    location = models.CharField(max_length=200)
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='on_site'
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=False, help_text="Currently working here")
    description = models.TextField()
    responsibilities = models.JSONField(
        default=list,
        help_text="List of responsibilities"
    )
    achievements = models.JSONField(
        default=list,
        help_text="List of achievements"
    )
    technologies = models.JSONField(
        default=list,
        help_text="Technologies used in this role"
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)
