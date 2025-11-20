from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Skill
from .serializers import (
    SkillListSerializer,
    SkillDetailSerializer,
    SkillCreateUpdateSerializer
)
from portfolio_api.permissions import IsSuperAdminOrEditor


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skills
    
    Public access for viewing (GET)
    Authentication required for create/update/delete
    """
    queryset = Skill.objects.select_related('profile').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['profile', 'category', 'proficiency_level']
    search_fields = ['name']
    ordering_fields = ['name', 'category', 'proficiency_level', 'years_of_experience', 'endorsements', 'order']
    ordering = ['category', 'order', '-proficiency_level']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SkillListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SkillCreateUpdateSerializer
        return SkillDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='by_profile/(?P<profile_id>[^/.]+)')
    def by_profile(self, request, profile_id=None):
        """Get all skills for a specific profile"""
        queryset = self.get_queryset().filter(profile__id=profile_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SkillListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = SkillListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get skills grouped by category"""
        categories = Skill.CATEGORY_CHOICES
        result = {}
        
        profile_id = request.query_params.get('profile')
        queryset = self.get_queryset()
        
        if profile_id:
            queryset = queryset.filter(profile__id=profile_id)
        
        for category_code, category_name in categories:
            skills = queryset.filter(category=category_code)
            if skills.exists():
                result[category_code] = {
                    'name': category_name,
                    'count': skills.count(),
                    'skills': SkillListSerializer(skills, many=True, context={'request': request}).data
                }
        
        return Response(result)
