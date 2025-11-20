from rest_framework import status, generics, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count
from django.utils import timezone

from .models import ContactMessage, MessageReply, MessageStatus
from .serializers import (
    ContactMessageSerializer, ContactMessageCreateSerializer,
    ContactMessageListSerializer, ContactMessageAdminSerializer,
    MessageReplySerializer, MessageReplyCreateSerializer,
    MessageStatsSerializer
)
from portfolio_api.permissions import IsEditorOrAbove, IsSuperAdmin, IsOwnerOrAdmin
from accounts.views import log_user_activity
from rest_framework.decorators import api_view, permission_classes, authentication_classes


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for contact messages
    
    Public can create messages (POST) - NO authentication required!
    Authentication required to view/manage messages
    """
    # Keep authentication available for admin actions
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    # No default permission - will be set by get_permissions
    permission_classes = []
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        elif self.action == 'list':
            return ContactMessageListSerializer
        elif self.action in ['update_status', 'update_admin']:
            return ContactMessageAdminSerializer
        return ContactMessageSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            # Anyone can send a contact message (public form) - NO AUTH REQUIRED!
            return [AllowAny()]
        # All other actions require authentication
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ContactMessage.objects.all()
        
        # Anonymous users cannot access queryset
        if not user.is_authenticated:
            return queryset.none()
        
        # Regular users see only their own messages
        # Editors and admins see all messages
        if not user.can_edit():
            queryset = queryset.filter(sender=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by message type
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority == 'true':
            queryset = queryset.filter(priority=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(message__icontains=search) |
                Q(sender__email__icontains=search)
            )
        
        return queryset.select_related('sender', 'responded_by')
    
    def perform_create(self, serializer):
        # Capture IP and user agent
        # Sender is optional (anonymous contact form)
        sender = self.request.user if self.request.user.is_authenticated else None
        
        message = serializer.save(
            sender=sender,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        if sender:
            log_user_activity(
                sender,
                'MESSAGE_SENT',
                self.request,
                {'message_id': str(message.id), 'type': message.message_type}
            )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark as read if accessed by admin
        if request.user.can_edit() and instance.status == MessageStatus.NEW:
            instance.mark_as_read()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsEditorOrAbove])
    def update_status(self, request, pk=None):
        """Update message status (admin only)"""
        message = self.get_object()
        serializer = ContactMessageAdminSerializer(
            message,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        log_user_activity(
            request.user,
            'MESSAGE_STATUS_UPDATED',
            request,
            {'message_id': str(message.id), 'new_status': message.status}
        )
        
        return Response({
            'message': 'Status updated successfully',
            'data': ContactMessageSerializer(message).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsEditorOrAbove])
    def mark_responded(self, request, pk=None):
        """Mark message as responded"""
        message = self.get_object()
        message.mark_as_responded(request.user)
        
        log_user_activity(
            request.user,
            'MESSAGE_RESPONDED',
            request,
            {'message_id': str(message.id)}
        )
        
        return Response({
            'message': 'Message marked as responded',
            'data': ContactMessageSerializer(message).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsEditorOrAbove])
    def statistics(self, request):
        """Get message statistics (admin only)"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        new = queryset.filter(status=MessageStatus.NEW).count()
        in_progress = queryset.filter(status=MessageStatus.IN_PROGRESS).count()
        responded = queryset.filter(status=MessageStatus.RESPONDED).count()
        priority = queryset.filter(priority=True).count()
        
        by_type = {}
        type_counts = queryset.values('message_type').annotate(count=Count('id'))
        for item in type_counts:
            by_type[item['message_type']] = item['count']
        
        stats = {
            'total_messages': total,
            'new_messages': new,
            'in_progress': in_progress,
            'responded': responded,
            'priority_count': priority,
            'by_type': by_type
        }
        
        serializer = MessageStatsSerializer(stats)
        return Response(serializer.data)


class MessageReplyViewSet(viewsets.ModelViewSet):
    """ViewSet for message replies"""
    serializer_class = MessageReplySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        message_id = self.request.query_params.get('message_id')
        
        queryset = MessageReply.objects.all()
        
        if message_id:
            queryset = queryset.filter(message_id=message_id)
        
        # Regular users cannot see internal notes
        if not user.can_edit():
            queryset = queryset.filter(
                Q(message__sender=user) | Q(author=user),
                is_internal=False
            )
        
        return queryset.select_related('message', 'author')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageReplyCreateSerializer
        return MessageReplySerializer
    
    def perform_create(self, serializer):
        message_id = self.request.data.get('message_id')
        
        try:
            message = ContactMessage.objects.get(id=message_id)
            
            # Check permissions
            if not self.request.user.can_edit() and message.sender != self.request.user:
                raise PermissionError("Cannot reply to this message")
            
            reply = serializer.save(
                author=self.request.user,
                message=message
            )
            
            log_user_activity(
                self.request.user,
                'MESSAGE_REPLY_CREATED',
                self.request,
                {'message_id': str(message.id), 'reply_id': str(reply.id)}
            )
        except ContactMessage.DoesNotExist:
            raise serializers.ValidationError("Invalid message_id")


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def public_contact_submit(request):
    """
    Public endpoint for anonymous contact form submissions
    NO authentication required!
    
    POST /api/contacts/submit/
    """
    serializer = ContactMessageCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Create the message
        message = serializer.save(
            sender=None,  # Anonymous submission
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Your message has been received! We will get back to you soon.',
            'id': str(message.id),
            'status': 'success'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Failed to submit contact form',
        'errors': serializer.errors,
        'status': 'error'
    }, status=status.HTTP_400_BAD_REQUEST)
