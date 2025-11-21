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
    queryset = Skill.objects.select_related('user').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'category', 'proficiency_level']
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
    
    def perform_create(self, serializer):
        """Auto-assign authenticated user when creating"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='by_user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all skills for a specific user"""
        queryset = self.get_queryset().filter(user__id=user_id)
        
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
        
        user_id = request.query_params.get('user')
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        for category_code, category_name in categories:
            skills = queryset.filter(category=category_code)
            if skills.exists():
                result[category_code] = {
                    'name': category_name,
                    'count': skills.count(),
                    'skills': SkillListSerializer(skills, many=True, context={'request': request}).data
                }
        
        return Response(result)
