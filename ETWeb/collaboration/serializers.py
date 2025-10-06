"""
Serializers for collaboration API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Organization, Team, TeamMembership, Task, TaskTimeEntry,
    ChatChannel, ChatMessage, Meeting, MeetingAttendance,
    Notification, ActivityMetrics, Integration
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OrganizationSerializer(serializers.ModelSerializer):
    team_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'team_count', 'created_at']
    
    def get_team_count(self, obj):
        return obj.teams.count()

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['user', 'role', 'joined_at']

class TeamSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    memberships = TeamMembershipSerializer(source='teammembership_set', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'organization', 'lead', 'memberships', 'member_count', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reporter = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reporter', 'team', 'estimated_hours', 'actual_hours',
            'progress_percentage', 'due_date', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_progress_percentage(self, obj):
        if obj.estimated_hours and obj.estimated_hours > 0:
            return min((float(obj.actual_hours) / float(obj.estimated_hours)) * 100, 100)
        return 0

class TaskTimeEntrySerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskTimeEntry
        fields = [
            'id', 'task', 'user', 'start_time', 'end_time', 'duration_minutes',
            'description', 'activity_score', 'screenshot_count', 'created_at'
        ]

class ChatChannelSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatChannel
        fields = ['id', 'name', 'description', 'channel_type', 'team', 'members', 'is_private', 'message_count', 'created_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    parent_message = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'channel', 'sender', 'content', 'parent_message', 'reply_count',
            'is_edited', 'edited_at', 'created_at', 'reactions'
        ]
    
    def get_parent_message(self, obj):
        if obj.parent_message:
            return {
                'id': obj.parent_message.id,
                'content': obj.parent_message.content[:50] + '...' if len(obj.parent_message.content) > 50 else obj.parent_message.content,
                'sender': obj.parent_message.sender.username
            }
        return None
    
    def get_reply_count(self, obj):
        return obj.replies.count()

class MeetingAttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MeetingAttendance
        fields = [
            'user', 'status', 'joined_at', 'left_at', 'duration_minutes',
            'engagement_score', 'attention_score'
        ]

class MeetingSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    attendance = MeetingAttendanceSerializer(source='meetingattendance_set', many=True, read_only=True)
    attendee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'status', 'start_time', 'end_time',
            'timezone', 'organizer', 'team', 'attendance', 'attendee_count',
            'zoom_meeting_id', 'meeting_url', 'created_at'
        ]
    
    def get_attendee_count(self, obj):
        return obj.attendees.count()

class NotificationSerializer(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()
    invitation = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'project', 'invitation',
            'data', 'is_read', 'read_at', 'created_at', 'related_object_id',
            'related_object_type', 'action_url'
        ]

    def get_project(self, obj):
        if obj.project:
            return {
                'id': obj.project.id,
                'name': obj.project.name
            }
        return None

    def get_invitation(self, obj):
        if obj.invitation_token:
            return {
                'token': obj.invitation_token.key,
                'accepted': obj.invitation_token.accepted
            }
        return None

class ActivityMetricsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    efficiency_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityMetrics
        fields = [
            'id', 'user', 'date', 'total_work_minutes', 'active_minutes', 'idle_minutes',
            'tasks_completed', 'tasks_started', 'meetings_attended', 'chat_messages_sent',
            'screenshots_taken', 'applications_used', 'websites_visited',
            'productivity_score', 'engagement_score', 'collaboration_score',
            'efficiency_ratio', 'created_at'
        ]
    
    def get_efficiency_ratio(self, obj):
        if obj.total_work_minutes > 0:
            return (obj.active_minutes / obj.total_work_minutes) * 100
        return 0

class IntegrationSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    
    class Meta:
        model = Integration
        fields = [
            'id', 'organization', 'integration_type', 'name', 'is_active',
            'last_sync', 'created_at', 'updated_at'
        ]
        # Exclude sensitive fields like credentials
