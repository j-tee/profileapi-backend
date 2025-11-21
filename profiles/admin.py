from django.contrib import admin
from .models import Profile, SocialLink


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ['platform', 'url', 'display_name', 'order']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_owner_name', 'headline', 'city', 'state', 'country', 'created_at']
    list_filter = ['country', 'state', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'headline']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [SocialLinkInline]
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Owner', {
            'fields': ('id', 'user')
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
    
    def get_owner_name(self, obj):
        return obj.user.full_name
    get_owner_name.short_description = 'Owner'
    get_owner_name.admin_order_field = 'user__first_name'


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'platform', 'url', 'order']
    list_filter = ['platform']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'url']
    readonly_fields = ['id']
