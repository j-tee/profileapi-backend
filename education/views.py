from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Education
from .serializers import (
    EducationListSerializer,
    EducationDetailSerializer,
    EducationCreateUpdateSerializer
)
from portfolio_api.permissions import IsSuperAdminOrEditor


class EducationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing education
    
    Public access for viewing (GET)
    Authentication required for create/update/delete
    """
    queryset = Education.objects.select_related('user').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'current']
    search_fields = ['institution', 'degree', 'field_of_study', 'description']
    ordering_fields = ['start_date', 'created_at', 'order', 'institution']
    ordering = ['-start_date', 'order']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return EducationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EducationCreateUpdateSerializer
        return EducationDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='by_user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all education for a specific user"""
        queryset = self.get_queryset().filter(user__id=user_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EducationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = EducationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
