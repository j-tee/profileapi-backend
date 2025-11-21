from rest_framework import serializers
from .models import Education
from django.utils import timezone


class EducationListSerializer(serializers.ModelSerializer):
    """Serializer for listing education (minimal data)"""
    duration = serializers.SerializerMethodField()
    institution_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'institution_display', 'degree',
            'field_of_study', 'start_date', 'end_date', 'current',
            'grade', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration(self, obj):
        """Calculate education duration"""
        start = obj.start_date
        end = obj.end_date if not obj.current else timezone.now().date()
        
        if start and end:
            delta = end - start
            years = delta.days // 365
            if years < 1:
                return "Less than a year"
            elif years == 1:
                return "1 year"
            return f"{years} years"
        return None
    
    def get_institution_display(self, obj):
        """Format institution display"""
        return f"{obj.institution} - {obj.field_of_study}"


class EducationDetailSerializer(serializers.ModelSerializer):
    """Serializer for education details (complete data)"""
    duration = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Education
        fields = [
            'id', 'user', 'owner_name', 'owner_email', 'institution', 'degree',
            'field_of_study', 'start_date', 'end_date', 'current',
            'grade', 'description', 'activities', 'achievements',
            'order', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name', 'owner_email']
    
    def get_duration(self, obj):
        """Calculate education duration"""
        start = obj.start_date
        end = obj.end_date if not obj.current else timezone.now().date()
        
        if start and end:
            delta = end - start
            years = delta.days // 365
            if years < 1:
                return "Less than a year"
            elif years == 1:
                return "1 year"
            return f"{years} years"
        return None
    
    def get_owner_name(self, obj):
        """Get education owner name"""
        if obj.user:
            return obj.user.get_full_name()
        return None
    
    def get_owner_email(self, obj):
        """Get education owner email"""
        if obj.user:
            return obj.user.email
        return None


class EducationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating education"""
    
    class Meta:
        model = Education
        fields = [
            'user', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'current', 'grade',
            'description', 'activities', 'achievements', 'order'
        ]
    
    def validate(self, data):
        """Validate education data"""
        # If currently studying, end_date should be None
        if data.get('current') and data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date must be empty if currently studying'
            })
        
        # If not current, end_date should be provided
        if not data.get('current') and not data.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'End date is required for completed education'
            })
        
        # End date should not be before start date
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be before start date'
                })
        
        # Activities should be a list
        if 'activities' in data and data['activities'] is not None:
            if not isinstance(data['activities'], list):
                raise serializers.ValidationError({
                    'activities': 'Activities must be a list'
                })
        
        # Achievements should be a list
        if 'achievements' in data and data['achievements'] is not None:
            if not isinstance(data['achievements'], list):
                raise serializers.ValidationError({
                    'achievements': 'Achievements must be a list'
                })
        
        return data
