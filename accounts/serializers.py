from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserActivity, UserRole
import qrcode
import io
import base64


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone'),
            role=UserRole.VIEWER  # Default role
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    mfa_token = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text="6-digit MFA token if MFA is enabled"
    )
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        mfa_token = attrs.get('mfa_token', '')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
            
            # Check MFA if enabled
            if user.mfa_enabled:
                if not mfa_token:
                    raise serializers.ValidationError({
                        'mfa_required': True,
                        'message': 'MFA token required'
                    })
                
                # Verify token or backup code
                if not (user.verify_totp(mfa_token) or user.verify_backup_code(mfa_token)):
                    raise serializers.ValidationError(
                        'Invalid MFA token or backup code.',
                        code='authorization'
                    )
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'is_verified', 'is_active',
            'mfa_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (admin only)"""
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role',
            'is_verified', 'is_active', 'mfa_enabled',
            'last_login', 'created_at'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user role (super admin only)"""
    role = serializers.ChoiceField(choices=UserRole.choices)


class MFASetupSerializer(serializers.Serializer):
    """Serializer for MFA setup response"""
    secret = serializers.CharField(read_only=True)
    qr_code = serializers.CharField(read_only=True)
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )


class MFAVerifySerializer(serializers.Serializer):
    """Serializer for verifying MFA setup"""
    token = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_token(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Token must be 6 digits")
        return value


class MFADisableSerializer(serializers.Serializer):
    """Serializer for disabling MFA"""
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity logs"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user_email', 'action', 'ip_address',
            'user_agent', 'details', 'timestamp'
        ]
        read_only_fields = fields
