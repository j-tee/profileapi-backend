from django.db import models
from django.conf import settings
import uuid


class MessageType(models.TextChoices):
    """Types of messages users can send"""
    GENERAL_INQUIRY = 'general', 'General Inquiry'
    PROJECT_PROPOSAL = 'proposal', 'Project Proposal'
    JOB_OPPORTUNITY = 'job', 'Job Opportunity'
    COLLABORATION = 'collaboration', 'Collaboration'
    FEEDBACK = 'feedback', 'Feedback'
    OTHER = 'other', 'Other'


class MessageStatus(models.TextChoices):
    """Status of contact messages"""
    NEW = 'new', 'New'
    READ = 'read', 'Read'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESPONDED = 'responded', 'Responded'
    ARCHIVED = 'archived', 'Archived'


class ContactMessage(models.Model):
    """
    Contact messages and proposals from authenticated users
    Only authenticated users can send messages to prevent spam
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        blank=True,
        null=True,
        help_text="Authenticated user who sent the message (optional for anonymous contact forms)"
    )
    
    # Anonymous sender info (for public contact forms)
    sender_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name for anonymous submissions")
    sender_email = models.EmailField(blank=True, null=True, help_text="Email for anonymous submissions")
    
    # Message details
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.GENERAL_INQUIRY
    )
    subject = models.CharField(max_length=200)
    message = models.TextField(help_text="Main message content")
    
    # Optional fields for proposals
    project_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Budget for project proposals"
    )
    project_timeline = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Expected timeline for project"
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of attachment URLs"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.NEW
    )
    priority = models.BooleanField(default=False, help_text="Mark as priority")
    
    # Response tracking
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes (only visible to admins)"
    )
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='responded_messages',
        blank=True,
        null=True
    )
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of sender"
    )
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        indexes = [
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['message_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        if self.sender:
            return f"{self.sender.email} - {self.subject}"
        return f"{self.sender_email or 'Anonymous'} - {self.subject}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if self.status == MessageStatus.NEW:
            self.status = MessageStatus.READ
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_responded(self, user):
        """Mark message as responded"""
        from django.utils import timezone
        self.status = MessageStatus.RESPONDED
        self.responded_by = user
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_by', 'responded_at', 'updated_at'])


class MessageReply(models.Model):
    """
    Replies to contact messages
    Maintains conversation thread
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        ContactMessage,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_replies'
    )
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal note not visible to message sender"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message Reply'
        verbose_name_plural = 'Message Replies'
    
    def __str__(self):
        return f"Reply to {self.message.subject} by {self.author.email}"
