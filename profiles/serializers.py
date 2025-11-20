from rest_framework import serializers
from .models import Profile, SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for social media links"""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = SocialLink
        fields = [
            'id', 'platform', 'platform_display', 'url', 
            'display_name', 'order'
        ]
        read_only_fields = ['id']


class ProfileListSerializer(serializers.ModelSerializer):
    """Serializer for profile list view"""
    full_name = serializers.CharField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 
            'headline', 'email', 'city', 'state', 'country',
            'profile_picture_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for profile detail view"""
    full_name = serializers.CharField(read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    
    # Count related items
    projects_count = serializers.SerializerMethodField()
    experiences_count = serializers.SerializerMethodField()
    education_count = serializers.SerializerMethodField()
    skills_count = serializers.SerializerMethodField()
    certifications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'headline', 'summary', 'email', 'phone',
            'city', 'state', 'country',
            'profile_picture', 'profile_picture_url',
            'cover_image', 'cover_image_url',
            'social_links',
            'projects_count', 'experiences_count', 'education_count',
            'skills_count', 'certifications_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
        return None
    
    def get_projects_count(self, obj):
        return obj.projects.count()
    
    def get_experiences_count(self, obj):
        return obj.experiences.count()
    
    def get_education_count(self, obj):
        return obj.education.count()
    
    def get_skills_count(self, obj):
        return obj.skills.count()
    
    def get_certifications_count(self, obj):
        return obj.certifications.count()


class ProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating profiles"""
    
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'headline', 'summary',
            'email', 'phone', 'city', 'state', 'country',
            'profile_picture', 'cover_image'
        ]
    
    def validate_email(self, value):
        """Ensure email is unique"""
        profile_id = self.instance.id if self.instance else None
        if Profile.objects.filter(email=value).exclude(id=profile_id).exists():
            raise serializers.ValidationError("A profile with this email already exists.")
        return value


class SocialLinkCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating social links"""
    
    class Meta:
        model = SocialLink
        fields = ['platform', 'url', 'display_name', 'order']
    
    def validate(self, data):
        """Check for duplicate platform/url combination"""
        profile = self.context.get('profile')
        social_link_id = self.instance.id if self.instance else None
        
        if profile:
            existing = SocialLink.objects.filter(
                profile=profile,
                platform=data.get('platform'),
                url=data.get('url')
            ).exclude(id=social_link_id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "This social link already exists for this profile."
                )
        
        return data
