from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import qrcode
import io
import base64

from .models import User, UserActivity, UserRole
from .serializers import (
    UserRegistrationSerializer, LoginSerializer, UserSerializer,
    UserListSerializer, UserUpdateSerializer, UserRoleUpdateSerializer,
    MFASetupSerializer, MFAVerifySerializer, MFADisableSerializer,
    PasswordChangeSerializer, UserActivitySerializer
)
from portfolio_api.permissions import IsSuperAdmin
from .signals import ensure_user_has_profile

User = get_user_model()


def log_user_activity(user, action, request, details=None):
    """Helper function to log user activities"""
    UserActivity.objects.create(
        user=user,
        action=action,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=details or {}
    )


class AuthThrottle(AnonRateThrottle):
    """Custom throttle for auth endpoints"""
    rate = '10/hour'


@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='dispatch')
class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        log_user_activity(user, 'USER_REGISTERED', request)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='dispatch')
class LoginView(generics.GenericAPIView):
    """User login endpoint with MFA support"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip'])
        
        log_user_activity(user, 'USER_LOGIN', request)
        
        # Ensure user has a profile (create if missing) and capture completion status
        profile = ensure_user_has_profile(user)
        profile_status = profile.completion_status()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'profile': {
                'id': str(profile.id),
                'email': profile.email,
                'full_name': profile.full_name,
                'headline': profile.headline
            },
            'profile_status': profile_status,
            'requires_profile_update': profile_status['needs_update'],
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        log_user_activity(request.user, 'PROFILE_UPDATED', request)
        return response


class UserPortfolioProfileView(generics.GenericAPIView):
    """Get the portfolio profile associated with the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's portfolio profile"""
        from profiles.models import Profile
        from profiles.serializers import ProfileDetailSerializer
        
        # Ensure profile exists
        profile = ensure_user_has_profile(request.user)
        
        serializer = ProfileDetailSerializer(profile, context={'request': request})
        return Response({
            'profile': serializer.data,
            'profile_status': profile.completion_status()
        })
    
    def post(self, request):
        """Create or ensure profile exists for current user"""
        from profiles.models import Profile
        from profiles.serializers import ProfileDetailSerializer
        
        # Ensure profile exists
        profile = ensure_user_has_profile(request.user)
        
        log_user_activity(request.user, 'PROFILE_ACCESSED', request)
        
        serializer = ProfileDetailSerializer(profile, context={'request': request})
        return Response({
            'message': 'Profile ready',
            'profile': serializer.data,
            'profile_status': profile.completion_status()
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management (admin only)"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['patch'], permission_classes=[IsSuperAdmin])
    def update_role(self, request, pk=None):
        """Update user role"""
        user = self.get_object()
        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_role = user.role
        user.role = serializer.validated_data['role']
        user.save(update_fields=['role'])
        
        log_user_activity(
            request.user,
            'USER_ROLE_UPDATED',
            request,
            {'target_user': user.email, 'old_role': old_role, 'new_role': user.role}
        )
        
        return Response({
            'message': 'User role updated successfully',
            'user': UserSerializer(user).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def deactivate(self, request, pk=None):
        """Deactivate user account"""
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        log_user_activity(
            request.user,
            'USER_DEACTIVATED',
            request,
            {'target_user': user.email}
        )
        
        return Response({'message': 'User deactivated successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def activate(self, request, pk=None):
        """Activate user account"""
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        log_user_activity(
            request.user,
            'USER_ACTIVATED',
            request,
            {'target_user': user.email}
        )
        
        return Response({'message': 'User activated successfully'})


class MFASetupView(generics.GenericAPIView):
    """Setup MFA for user account"""
    permission_classes = [IsAuthenticated]
    serializer_class = MFASetupSerializer
    
    def post(self, request):
        user = request.user
        
        if user.mfa_enabled:
            return Response(
                {'error': 'MFA is already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        secret = user.generate_mfa_secret()
        backup_codes = user.generate_backup_codes()
        
        totp_uri = user.get_totp_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        log_user_activity(user, 'MFA_SETUP_INITIATED', request)
        
        return Response({
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'backup_codes': backup_codes,
            'message': 'Scan the QR code with your authenticator app and verify with a token'
        })


class MFAVerifyView(generics.GenericAPIView):
    """Verify and enable MFA"""
    permission_classes = [IsAuthenticated]
    serializer_class = MFAVerifySerializer
    
    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        if user.verify_totp(token):
            user.mfa_enabled = True
            user.save(update_fields=['mfa_enabled'])
            
            log_user_activity(user, 'MFA_ENABLED', request)
            
            return Response({
                'message': 'MFA enabled successfully',
                'mfa_enabled': True
            })
        else:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MFADisableView(generics.GenericAPIView):
    """Disable MFA for user account"""
    permission_classes = [IsAuthenticated]
    serializer_class = MFADisableSerializer
    
    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['password']):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.mfa_enabled = False
        user.mfa_secret = None
        user.backup_codes = []
        user.save(update_fields=['mfa_enabled', 'mfa_secret', 'backup_codes'])
        
        log_user_activity(user, 'MFA_DISABLED', request)
        
        return Response({'message': 'MFA disabled successfully'})


class PasswordChangeView(generics.GenericAPIView):
    """Change user password"""
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        log_user_activity(user, 'PASSWORD_CHANGED', request)
        
        return Response({'message': 'Password changed successfully'})


class UserActivityListView(generics.ListAPIView):
    """List user activities"""
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin():
            queryset = UserActivity.objects.all()
            
            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            action = self.request.query_params.get('action')
            if action:
                queryset = queryset.filter(action__icontains=action)
        else:
            queryset = UserActivity.objects.filter(user=user)
        
        return queryset
