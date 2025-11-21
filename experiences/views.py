from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Experience
from .serializers import (
    ExperienceListSerializer,
    ExperienceDetailSerializer,
    ExperienceCreateUpdateSerializer
)
from portfolio_api.permissions import IsSuperAdminOrEditor


class ExperienceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing work experiences
    
    Public access for viewing (GET)
    Authentication required for create/update/delete
    """
    queryset = Experience.objects.select_related('user').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'employment_type', 'location_type', 'current']
    search_fields = ['title', 'company', 'description', 'technologies']
    ordering_fields = ['start_date', 'created_at', 'order', 'company']
    ordering = ['-start_date', 'order']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ExperienceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ExperienceCreateUpdateSerializer
        return ExperienceDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='by_user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all experiences for a specific user"""
        queryset = self.get_queryset().filter(user__id=user_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ExperienceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ExperienceListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current work experiences only"""
        queryset = self.get_queryset().filter(current=True)
        serializer = ExperienceListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
