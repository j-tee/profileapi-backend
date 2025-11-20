from django.contrib import admin
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    """Inline admin for project images"""
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']
    ordering = ['order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects"""
    list_display = [
        'title', 'profile', 'role', 'start_date', 'end_date', 
        'current', 'featured', 'order', 'created_at'
    ]
    list_filter = ['featured', 'current', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'role', 'technologies']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-featured', '-start_date', 'order']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'profile', 'title', 'description', 'long_description')
        }),
        ('Project Details', {
            'fields': (
                'technologies', 'role', 'team_size', 
                'start_date', 'end_date', 'current'
            )
        }),
        ('URLs & Media', {
            'fields': ('project_url', 'github_url', 'demo_url', 'video')
        }),
        ('Additional Information', {
            'fields': ('highlights', 'challenges', 'outcomes'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('featured', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProjectImageInline]
    
    def save_model(self, request, obj, form, change):
        """Auto-manage end_date based on current status"""
        if obj.current:
            obj.end_date = None
        super().save_model(request, obj, form, change)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """Admin interface for project images"""
    list_display = ['project', 'caption', 'order', 'uploaded_at']
    list_filter = ['project', 'uploaded_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['project', 'order']
