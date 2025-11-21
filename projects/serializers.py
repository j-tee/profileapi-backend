from rest_framework import serializers
from .models import Project, ProjectImage
from django.utils import timezone


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer for project images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectImage
        fields = [
            'id', 'image', 'image_url', 'caption', 
            'order', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'image_url']
    
    def get_image_url(self, obj):
        """Get full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects (minimal data)"""
    thumbnail = serializers.SerializerMethodField()
    technologies_count = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'role', 
            'technologies', 'technologies_count', 'start_date', 
            'end_date', 'current', 'featured', 'thumbnail',
            'project_url', 'github_url', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_thumbnail(self, obj):
        """Get first image as thumbnail"""
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None
    
    def get_technologies_count(self, obj):
        """Count of technologies"""
        return len(obj.technologies) if obj.technologies else 0
    
    def get_duration(self, obj):
        """Calculate project duration"""
        start = obj.start_date
        end = obj.end_date if not obj.current else timezone.now().date()
        
        if start and end:
            delta = end - start
            months = delta.days // 30
            if months < 1:
                return "Less than a month"
            elif months == 1:
                return "1 month"
            elif months < 12:
                return f"{months} months"
            else:
                years = months // 12
                remaining_months = months % 12
                if remaining_months == 0:
                    return f"{years} year{'s' if years > 1 else ''}"
                return f"{years} year{'s' if years > 1 else ''} {remaining_months} month{'s' if remaining_months > 1 else ''}"
        return None


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project details (complete data)"""
    images = ProjectImageSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    technologies_count = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'user', 'owner_name', 'owner_email', 'title', 'description', 
            'long_description', 'technologies', 'technologies_count',
            'role', 'team_size', 'start_date', 'end_date', 'current',
            'project_url', 'github_url', 'demo_url', 'video', 'video_url',
            'highlights', 'challenges', 'outcomes', 'featured', 'order',
            'images', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name', 'owner_email', 'video_url']
    
    def get_duration(self, obj):
        """Calculate project duration"""
        start = obj.start_date
        end = obj.end_date if not obj.current else timezone.now().date()
        
        if start and end:
            delta = end - start
            months = delta.days // 30
            if months < 1:
                return "Less than a month"
            elif months == 1:
                return "1 month"
            elif months < 12:
                return f"{months} months"
            else:
                years = months // 12
                remaining_months = months % 12
                if remaining_months == 0:
                    return f"{years} year{'s' if years > 1 else ''}"
                return f"{years} year{'s' if years > 1 else ''} {remaining_months} month{'s' if remaining_months > 1 else ''}"
        return None
    
    def get_technologies_count(self, obj):
        """Count of technologies"""
        return len(obj.technologies) if obj.technologies else 0
    
    def get_owner_name(self, obj):
        """Get project owner name"""
        if obj.user:
            return obj.user.get_full_name()
        return None
    
    def get_owner_email(self, obj):
        """Get project owner email"""
        if obj.user:
            return obj.user.email
        return None
    
    def get_video_url(self, obj):
        """Get full URL for video"""
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating projects"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'long_description',
            'technologies', 'role', 'team_size', 'start_date',
            'end_date', 'current', 'project_url', 'github_url',
            'demo_url', 'highlights', 'challenges', 'outcomes',
            'featured', 'order'
        ]
    
    def validate(self, data):
        """Validate project data"""
        # If current project, end_date should be None
        if data.get('current') and data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date must be empty for current projects'
            })
        
        # If not current, end_date should be provided
        if not data.get('current') and not data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date is required for completed projects'
            })
        
        # End date should not be before start date
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be before start date'
                })
        
        # Technologies should be a list
        if 'technologies' in data and not isinstance(data['technologies'], list):
            raise serializers.ValidationError({
                'technologies': 'Technologies must be a list'
            })
        
        # Highlights should be a list
        if 'highlights' in data and not isinstance(data['highlights'], list):
            raise serializers.ValidationError({
                'highlights': 'Highlights must be a list'
            })
        
        return data


class ProjectImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading project images"""
    
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption', 'order']
    
    def validate_image(self, value):
        """Validate image file"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Image size must not exceed 10MB')
        
        # Check file type
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        extension = value.name.split('.')[-1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(
                f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
            )
        
        return value
