from rest_framework import serializers
from .models import Skill


class SkillListSerializer(serializers.ModelSerializer):
    """Serializer for listing skills (minimal data)"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'category_display',
            'proficiency_level', 'proficiency_display',
            'years_of_experience', 'endorsements', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SkillDetailSerializer(serializers.ModelSerializer):
    """Serializer for skill details (complete data)"""
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'user', 'owner_name', 'owner_email', 'name', 'category',
            'category_display', 'proficiency_level', 'proficiency_display',
            'years_of_experience', 'endorsements', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name', 'owner_email']
    
    def get_owner_name(self, obj):
        """Get skill owner name"""
        if obj.user:
            return obj.user.get_full_name()
        return None
    
    def get_owner_email(self, obj):
        """Get skill owner email"""
        if obj.user:
            return obj.user.email
        return None


class SkillCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating skills"""
    
    class Meta:
        model = Skill
        fields = [
            'name', 'category', 'proficiency_level',
            'years_of_experience', 'endorsements', 'order'
        ]
    
    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value < 0 or value > 50:
            raise serializers.ValidationError('Years of experience must be between 0 and 50')
        return value
    
    def validate_endorsements(self, value):
        """Validate endorsements"""
        if value < 0:
            raise serializers.ValidationError('Endorsements cannot be negative')
        return value
