from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models

from .models import Certification
from .serializers import (
    CertificationListSerializer,
    CertificationDetailSerializer,
    CertificationCreateUpdateSerializer
)
from portfolio_api.permissions import IsSuperAdminOrEditor


class CertificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing certifications
    
    Public access for viewing (GET)
    Authentication required for create/update/delete
    """
    queryset = Certification.objects.select_related('profile').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['profile', 'issuer']
    search_fields = ['name', 'issuer', 'description', 'skills']
    ordering_fields = ['issue_date', 'created_at', 'order', 'name']
    ordering = ['-issue_date', 'order']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CertificationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CertificationCreateUpdateSerializer
        return CertificationDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='by_profile/(?P<profile_id>[^/.]+)')
    def by_profile(self, request, profile_id=None):
        """Get all certifications for a specific profile"""
        queryset = self.get_queryset().filter(profile__id=profile_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CertificationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CertificationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active (non-expired) certifications"""
        now = timezone.now().date()
        queryset = self.get_queryset().filter(
            models.Q(expiration_date__isnull=True) | models.Q(expiration_date__gt=now)
        )
        serializer = CertificationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
