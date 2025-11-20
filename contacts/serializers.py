from rest_framework import serializers
from .models import ContactMessage, MessageReply, MessageType, MessageStatus
from accounts.serializers import UserSerializer


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating and viewing contact messages"""
    sender = UserSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    replied_by_name = serializers.CharField(
        source='responded_by.full_name',
        read_only=True,
        allow_null=True
    )
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'sender', 'sender_name', 'message_type', 'subject',
            'message', 'project_budget', 'project_timeline', 'attachments',
            'status', 'priority', 'admin_notes', 'responded_by',
            'replied_by_name', 'responded_at', 'reply_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'status', 'admin_notes',
            'responded_by', 'replied_by_name', 'responded_at',
            'created_at', 'updated_at'
        ]
    
    def get_reply_count(self, obj):
        return obj.replies.count()
    
    def validate(self, attrs):
        # Validate budget for proposal type
        if attrs.get('message_type') == MessageType.PROJECT_PROPOSAL:
            if not attrs.get('project_budget'):
                raise serializers.ValidationError(
                    {"project_budget": "Budget is required for project proposals."}
                )
        return attrs


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages (supports anonymous submissions)"""
    
    class Meta:
        model = ContactMessage
        fields = [
            'sender_name', 'sender_email', 'message_type', 'subject', 'message',
            'project_budget', 'project_timeline', 'attachments'
        ]
    
    def validate(self, attrs):
        # For anonymous submissions, require name and email
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            if not attrs.get('sender_name'):
                raise serializers.ValidationError(
                    {"sender_name": "Name is required for anonymous submissions."}
                )
            if not attrs.get('sender_email'):
                raise serializers.ValidationError(
                    {"sender_email": "Email is required for anonymous submissions."}
                )
        
        # Validate budget for proposal type
        if attrs.get('message_type') == MessageType.PROJECT_PROPOSAL:
            if not attrs.get('project_budget'):
                raise serializers.ValidationError(
                    {"project_budget": "Budget is required for project proposals."}
                )
        return attrs


class ContactMessageListSerializer(serializers.ModelSerializer):
    """Serializer for listing contact messages (simplified)"""
    sender_display_name = serializers.SerializerMethodField()
    sender_display_email = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'sender_display_name', 'sender_display_email', 'message_type',
            'subject', 'status', 'priority', 'reply_count',
            'created_at', 'updated_at'
        ]
    
    def get_sender_display_name(self, obj):
        """Get sender name from authenticated user or anonymous submission"""
        if obj.sender:
            return obj.sender.full_name
        return obj.sender_name or 'Anonymous'
    
    def get_sender_display_email(self, obj):
        """Get sender email from authenticated user or anonymous submission"""
        if obj.sender:
            return obj.sender.email
        return obj.sender_email
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin operations on messages"""
    
    class Meta:
        model = ContactMessage
        fields = ['status', 'priority', 'admin_notes']


class MessageReplySerializer(serializers.ModelSerializer):
    """Serializer for message replies"""
    author = UserSerializer(read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = MessageReply
        fields = [
            'id', 'message', 'author', 'author_name',
            'content', 'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'updated_at']


class MessageReplyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating message replies"""
    
    class Meta:
        model = MessageReply
        fields = ['content', 'is_internal']
    
    def validate(self, attrs):
        # Only admins can create internal notes
        request = self.context.get('request')
        if attrs.get('is_internal') and not request.user.can_edit():
            raise serializers.ValidationError(
                {"is_internal": "Only admins can create internal notes."}
            )
        return attrs


class MessageStatsSerializer(serializers.Serializer):
    """Serializer for message statistics"""
    total_messages = serializers.IntegerField()
    new_messages = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    responded = serializers.IntegerField()
    by_type = serializers.DictField()
    priority_count = serializers.IntegerField()
