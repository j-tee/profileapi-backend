from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import serializers as drf_serializers
from django.db.models import Q
from .models import Profile, SocialLink
from .serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileCreateUpdateSerializer,
    SocialLinkSerializer,
    SocialLinkCreateUpdateSerializer
)
from portfolio_api.permissions import IsSuperAdminOrEditor


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for profile management
    
    list: Get all profiles (public)
    retrieve: Get profile details (public)
    create: Create new profile (admin/editor only)
    update: Update profile (admin/editor only)
    delete: Delete profile (admin/editor only)
    """
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProfileCreateUpdateSerializer
        return ProfileDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        queryset = Profile.objects.all()
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(headline__icontains=search)
            )
        
        # Filter by location
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        state = self.request.query_params.get('state')
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        return queryset.select_related().prefetch_related('social_links')
    
    @action(detail=True, methods=['get'])
    def social_links(self, request, pk=None):
        """Get all social links for a profile"""
        profile = self.get_object()
        social_links = profile.social_links.all()
        serializer = SocialLinkSerializer(social_links, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperAdminOrEditor])
    def add_social_link(self, request, pk=None):
        """Add a social link to a profile"""
        profile = self.get_object()
        serializer = SocialLinkCreateUpdateSerializer(
            data=request.data,
            context={'request': request, 'profile': profile}
        )
        
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='social_links/(?P<link_id>[^/.]+)',
            permission_classes=[IsAuthenticated, IsSuperAdminOrEditor])
    def delete_social_link(self, request, pk=None, link_id=None):
        """Delete a social link from a profile"""
        profile = self.get_object()
        try:
            social_link = profile.social_links.get(id=link_id)
            social_link.delete()
            return Response(
                {'message': 'Social link deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except SocialLink.DoesNotExist:
            return Response(
                {'error': 'Social link not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """Get profile by email"""
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Email parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = Profile.objects.get(email=email)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get', 'patch', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get or update the authenticated user's own profile"""
        from accounts.signals import ensure_user_has_profile
        
        # Ensure profile exists for current user
        profile = ensure_user_has_profile(request.user)
        
        if request.method == 'GET':
            serializer = ProfileDetailSerializer(profile, context={'request': request})
            return Response({
                'profile': serializer.data,
                'profile_status': profile.completion_status()
            })
        
        # PATCH or PUT - update profile
        serializer = ProfileCreateUpdateSerializer(
            profile, 
            data=request.data, 
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'profile': ProfileDetailSerializer(profile, context={'request': request}).data,
                'profile_status': profile.completion_status()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for social link management
    """
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        queryset = SocialLink.objects.select_related('profile')
        
        # Filter by profile
        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)
        
        # Filter by platform
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set profile when creating social link"""
        profile_id = self.request.data.get('profile')
        if profile_id:
            try:
                profile = Profile.objects.get(id=profile_id)
                serializer.save(profile=profile)
            except Profile.DoesNotExist:
                raise drf_serializers.ValidationError({'profile': 'Profile not found'})
        else:
            raise drf_serializers.ValidationError({'profile': 'Profile ID is required'})
