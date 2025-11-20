from rest_framework import serializers
from .models import Certification


class CertificationListSerializer(serializers.ModelSerializer):
    """Serializer for listing certifications (minimal data)"""
    is_active = serializers.BooleanField(read_only=True)
    issuer_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'issuer', 'issuer_display', 'issue_date',
            'expiration_date', 'is_active', 'credential_url',
            'skills', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_issuer_display(self, obj):
        """Format issuer display"""
        if obj.credential_id:
            return f"{obj.issuer} (ID: {obj.credential_id})"
        return obj.issuer


class CertificationDetailSerializer(serializers.ModelSerializer):
    """Serializer for certification details (complete data)"""
    profile_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Certification
        fields = [
            'id', 'profile', 'profile_name', 'name', 'issuer',
            'issue_date', 'expiration_date', 'is_active',
            'credential_id', 'credential_url', 'description',
            'skills', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_name']
    
    def get_profile_name(self, obj):
        """Get profile owner name"""
        if obj.profile:
            return obj.profile.full_name
        return None


class CertificationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating certifications"""
    
    class Meta:
        model = Certification
        fields = [
            'profile', 'name', 'issuer', 'issue_date',
            'expiration_date', 'credential_id', 'credential_url',
            'description', 'skills', 'order'
        ]
    
    def validate(self, data):
        """Validate certification data"""
        # Expiration date should not be before issue date
        if data.get('issue_date') and data.get('expiration_date'):
            if data['expiration_date'] < data['issue_date']:
                raise serializers.ValidationError({
                    'expiration_date': 'Expiration date cannot be before issue date'
                })
        
        # Skills should be a list
        if 'skills' in data and not isinstance(data['skills'], list):
            raise serializers.ValidationError({
                'skills': 'Skills must be a list'
            })
        
        return data
