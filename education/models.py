from django.db import models
import uuid


class Education(models.Model):
    """
    Educational background
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name='education'
    )
    institution = models.CharField(max_length=200, help_text="School or university name")
    degree = models.CharField(max_length=200, help_text="Degree type (e.g., Bachelor's, Master's)")
    field_of_study = models.CharField(max_length=200, help_text="Major or field of study")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=False, help_text="Currently studying")
    grade = models.CharField(max_length=50, blank=True, null=True, help_text="GPA or grade")
    description = models.TextField(blank=True, null=True)
    activities = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Extracurricular activities"
    )
    achievements = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Academic achievements or honors"
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = 'Education'
        verbose_name_plural = 'Education'
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} - {self.institution}"
    
    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)
