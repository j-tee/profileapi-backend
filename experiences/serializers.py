from rest_framework import serializers
from .models import Experience
from django.utils import timezone


class ExperienceListSerializer(serializers.ModelSerializer):
    """Serializer for listing experiences (minimal data)"""
    duration = serializers.SerializerMethodField()
    company_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Experience
        fields = [
            'id', 'title', 'company', 'company_display', 'employment_type',
            'location', 'location_type', 'start_date', 'end_date', 'current',
            'duration', 'technologies', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration(self, obj):
        """Calculate experience duration"""
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
    
    def get_company_display(self, obj):
        """Format company display with location type"""
        if obj.location_type == 'remote':
            return f"{obj.company} (Remote)"
        elif obj.location_type == 'hybrid':
            return f"{obj.company} (Hybrid)"
        return obj.company


class ExperienceDetailSerializer(serializers.ModelSerializer):
    """Serializer for experience details (complete data)"""
    duration = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    
    class Meta:
        model = Experience
        fields = [
            'id', 'user', 'owner_name', 'owner_email', 'title', 'company',
            'employment_type', 'employment_type_display', 'location',
            'location_type', 'location_type_display', 'start_date',
            'end_date', 'current', 'description', 'responsibilities',
            'achievements', 'technologies', 'order', 'duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name', 'owner_email']
    
    def get_duration(self, obj):
        """Calculate experience duration"""
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
    
    def get_owner_name(self, obj):
        """Get experience owner name"""
        if obj.user:
            return obj.user.get_full_name()
        return None
    
    def get_owner_email(self, obj):
        """Get experience owner email"""
        if obj.user:
            return obj.user.email
        return None


class ExperienceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating experiences"""
    
    class Meta:
        model = Experience
        fields = [
            'user', 'title', 'company', 'employment_type', 'location',
            'location_type', 'start_date', 'end_date', 'current',
            'description', 'responsibilities', 'achievements',
            'technologies', 'order'
        ]
    
    def validate(self, data):
        """Validate experience data"""
        # If current experience, end_date should be None
        if data.get('current') and data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date must be empty for current positions'
            })
        
        # If not current, end_date should be provided
        if not data.get('current') and not data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date is required for past positions'
            })
        
        # End date should not be before start date
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be before start date'
                })
        
        # Responsibilities should be a list
        if 'responsibilities' in data and not isinstance(data['responsibilities'], list):
            raise serializers.ValidationError({
                'responsibilities': 'Responsibilities must be a list'
            })
        
        # Achievements should be a list
        if 'achievements' in data and not isinstance(data['achievements'], list):
            raise serializers.ValidationError({
                'achievements': 'Achievements must be a list'
            })
        
        # Technologies should be a list
        if 'technologies' in data and not isinstance(data['technologies'], list):
            raise serializers.ValidationError({
                'technologies': 'Technologies must be a list'
            })
        
        return data
