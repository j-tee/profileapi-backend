from django.contrib import admin
from .models import Profile, SocialLink


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ['platform', 'url', 'display_name', 'order']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'headline', 'city', 'state', 'country', 'created_at']
    list_filter = ['country', 'state', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'headline']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [SocialLinkInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Professional Details', {
            'fields': ('headline', 'summary')
        }),
        ('Location', {
            'fields': ('city', 'state', 'country')
        }),
        ('Media', {
            'fields': ('profile_picture', 'cover_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'platform', 'url', 'order']
    list_filter = ['platform']
    search_fields = ['profile__first_name', 'profile__last_name', 'url']
    readonly_fields = ['id']
