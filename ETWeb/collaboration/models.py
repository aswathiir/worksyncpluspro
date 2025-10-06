"""
Enhanced collaboration models for Employee Tracker
Integrates monitoring with team management, tasks, chat, and meetings
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Organization(models.Model):
    """Organization/Company model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Team(models.Model):
    """Team model for organizing employees"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"

class TeamMembership(models.Model):
    """Team membership with roles"""
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('lead', 'Team Lead'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'team']

class Task(models.Model):
    """Enhanced task model with monitoring integration"""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignments
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_tasks')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    
    # Time tracking
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.assignee}"

class TaskTimeEntry(models.Model):
    """Time tracking entries linked to monitoring data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    # Link to monitoring data
    activity_score = models.FloatField(default=0.0)  # From employee monitoring
    screenshot_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

class ChatChannel(models.Model):
    """Chat channels for teams"""
    CHANNEL_TYPES = [
        ('team', 'Team Channel'),
        ('project', 'Project Channel'),
        ('direct', 'Direct Message'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES, default='team')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_channels')
    members = models.ManyToManyField(User, related_name='chat_channels')
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"#{self.name}"

class ChatMessage(models.Model):
    """Chat messages with threading support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    
    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Reactions
    reactions = models.JSONField(default=dict, blank=True)  # {emoji: [user_ids]}
    
    class Meta:
        ordering = ['created_at']

class Meeting(models.Model):
    """Meeting model with monitoring integration"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Participants
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    attendees = models.ManyToManyField(User, through='MeetingAttendance', related_name='meetings')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings')
    
    # Integration
    zoom_meeting_id = models.CharField(max_length=255, blank=True)
    meeting_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MeetingAttendance(models.Model):
    """Meeting attendance tracking"""
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    # Attendance tracking
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    
    # Engagement metrics (from monitoring)
    engagement_score = models.FloatField(default=0.0)
    attention_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    """Notification system with project invitation support"""
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('chat_mention', 'Chat Mention'),
        ('activity_alert', 'Activity Alert'),
        ('project_invitation', 'Project Invitation'),  # Added project invitation type
        ('system', 'System Notification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Metadata
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # For project invitations
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    invitation_token = models.OneToOneField('projects.ProjectInvitationToken', on_delete=models.CASCADE, null=True, blank=True, related_name='notification')

    # Links and actions
    related_object_id = models.UUIDField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    action_url = models.URLField(blank=True)

    # Additional data
    data = models.JSONField(default=dict, blank=True)

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

class ActivityMetrics(models.Model):
    """Enhanced activity metrics combining monitoring data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_metrics')
    date = models.DateField()
    
    # Time tracking
    total_work_minutes = models.IntegerField(default=0)
    active_minutes = models.IntegerField(default=0)
    idle_minutes = models.IntegerField(default=0)
    
    # Productivity metrics
    tasks_completed = models.IntegerField(default=0)
    tasks_started = models.IntegerField(default=0)
    meetings_attended = models.IntegerField(default=0)
    chat_messages_sent = models.IntegerField(default=0)
    
    # Monitoring data
    screenshots_taken = models.IntegerField(default=0)
    applications_used = models.JSONField(default=list, blank=True)
    websites_visited = models.JSONField(default=list, blank=True)
    
    # Scores
    productivity_score = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    collaboration_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']

class Integration(models.Model):
    """Third-party integrations"""
    INTEGRATION_TYPES = [
        ('zoom', 'Zoom'),
        ('slack', 'Slack'),
        ('github', 'GitHub'),
        ('jira', 'Jira'),
        ('google_calendar', 'Google Calendar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='integrations')
    integration_type = models.CharField(max_length=30, choices=INTEGRATION_TYPES)
    name = models.CharField(max_length=255)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    credentials = models.JSONField(default=dict, blank=True)  # Encrypted in production
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AuditLog(models.Model):
    """Audit log for tracking changes"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=50)
    resource_id = models.UUIDField(null=True, blank=True)
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Changes
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
