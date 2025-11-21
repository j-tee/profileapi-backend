from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Project, ProjectImage
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    ProjectImageSerializer,
    ProjectImageUploadSerializer
)
from portfolio_api.permissions import IsOwnerOrReadOnly, IsSuperAdminOrEditor


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects
    
    List: GET /api/projects/
    Retrieve: GET /api/projects/{id}/
    Create: POST /api/projects/
    Update: PUT/PATCH /api/projects/{id}/
    Delete: DELETE /api/projects/{id}/
    
    Additional actions:
    - featured: GET /api/projects/featured/ - Get featured projects
    - by_profile: GET /api/projects/by_profile/{profile_id}/ - Get projects by profile
    - upload_images: POST /api/projects/{id}/upload_images/ - Upload project images
    - delete_image: DELETE /api/projects/{id}/delete_image/{image_id}/ - Delete project image
    - reorder_images: POST /api/projects/{id}/reorder_images/ - Reorder project images
    """
    queryset = Project.objects.select_related('user').prefetch_related('images').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSuperAdminOrEditor]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['featured', 'current', 'user']
    search_fields = ['title', 'description', 'long_description', 'technologies', 'role']
    ordering_fields = ['start_date', 'created_at', 'order', 'title']
    ordering = ['-featured', '-start_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload_images', 'delete_image', 'reorder_images']:
            return [IsSuperAdminOrEditor()]
        return [IsAuthenticatedOrReadOnly()]
    
    def list(self, request, *args, **kwargs):
        """List all projects with filtering and search"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by user if provided
        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        # Filter featured only
        featured_only = request.query_params.get('featured_only')
        if featured_only and featured_only.lower() == 'true':
            queryset = queryset.filter(featured=True)
        
        # Filter current projects
        current_only = request.query_params.get('current_only')
        if current_only and current_only.lower() == 'true':
            queryset = queryset.filter(current=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new project"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Handle video file if provided
        video = request.FILES.get('video')
        if video:
            # Validate video file
            if video.size > 100 * 1024 * 1024:  # 100MB max
                return Response(
                    {'error': 'Video size must not exceed 100MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            valid_video_extensions = ['mp4', 'mov', 'avi', 'webm', 'mkv']
            extension = video.name.split('.')[-1].lower()
            if extension not in valid_video_extensions:
                return Response(
                    {'error': f'Invalid video type. Allowed: {", ".join(valid_video_extensions)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        project = serializer.save(video=video if video else None)
        
        # Handle multiple image uploads
        images = request.FILES.getlist('images')
        if images:
            for idx, image in enumerate(images):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    order=idx
                )
        
        # Return detailed response
        response_serializer = ProjectDetailSerializer(project, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a project"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Handle video file if provided
        video = request.FILES.get('video')
        if video:
            # Validate video file
            if video.size > 100 * 1024 * 1024:  # 100MB max
                return Response(
                    {'error': 'Video size must not exceed 100MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            valid_video_extensions = ['mp4', 'mov', 'avi', 'webm', 'mkv']
            extension = video.name.split('.')[-1].lower()
            if extension not in valid_video_extensions:
                return Response(
                    {'error': f'Invalid video type. Allowed: {", ".join(valid_video_extensions)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete old video if exists
            if instance.video:
                instance.video.delete(save=False)
            
            instance.video = video
        
        project = serializer.save()
        
        # Return detailed response
        response_serializer = ProjectDetailSerializer(project, context={'request': request})
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured projects only"""
        queryset = self.get_queryset().filter(featured=True)
        serializer = ProjectListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by_user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all projects for a specific user"""
        queryset = self.get_queryset().filter(user__id=user_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProjectListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        """Upload multiple images for a project"""
        project = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get starting order number
        last_image = project.images.order_by('-order').first()
        start_order = last_image.order + 1 if last_image else 0
        
        created_images = []
        for idx, image in enumerate(images):
            # Validate image
            if image.size > 10 * 1024 * 1024:  # 10MB max
                continue
            
            caption = request.data.get(f'caption_{idx}', '')
            
            project_image = ProjectImage.objects.create(
                project=project,
                image=image,
                caption=caption,
                order=start_order + idx
            )
            created_images.append(project_image)
        
        serializer = ProjectImageSerializer(created_images, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='delete_image/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete a specific project image"""
        project = self.get_object()
        
        try:
            image = project.images.get(id=image_id)
            image.image.delete(save=False)  # Delete file from storage
            image.delete()  # Delete database record
            return Response(
                {'message': 'Image deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ProjectImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reorder_images(self, request, pk=None):
        """Reorder project images"""
        project = self.get_object()
        image_order = request.data.get('image_order', [])
        
        if not isinstance(image_order, list):
            return Response(
                {'error': 'image_order must be a list of image IDs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update order for each image
        for idx, image_id in enumerate(image_order):
            try:
                image = project.images.get(id=image_id)
                image.order = idx
                image.save()
            except ProjectImage.DoesNotExist:
                continue
        
        # Return updated project
        serializer = ProjectDetailSerializer(project, context={'request': request})
        return Response(serializer.data)
