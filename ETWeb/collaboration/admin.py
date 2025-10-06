"""
Django admin configuration for collaboration models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Organization, Team, TeamMembership, Task, TaskTimeEntry,
    ChatChannel, ChatMessage, Meeting, MeetingAttendance,
    Notification, ActivityMetrics, Integration, AuditLog
)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def team_count(self, obj):
        return obj.teams.count()
    team_count.short_description = 'Teams'

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    readonly_fields = ['joined_at']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'lead', 'member_count', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['name', 'description', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [TeamMembershipInline]
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assignee', 'team', 'due_date', 'progress']
    list_filter = ['status', 'priority', 'team', 'created_at']
    search_fields = ['title', 'description', 'assignee__username', 'team__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assignee', 'reporter', 'team')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours', 'due_date')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def progress(self, obj):
        if obj.estimated_hours and obj.estimated_hours > 0:
            progress_pct = min((float(obj.actual_hours) / float(obj.estimated_hours)) * 100, 100)
            color = 'green' if progress_pct <= 100 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, progress_pct
            )
        return '-'
    progress.short_description = 'Progress'

@admin.register(TaskTimeEntry)
class TaskTimeEntryAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'start_time', 'duration_minutes', 'activity_score']
    list_filter = ['user', 'start_time', 'task__team']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'start_time'

@admin.register(ChatChannel)
class ChatChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel_type', 'team', 'member_count', 'is_private', 'created_at']
    list_filter = ['channel_type', 'is_private', 'team', 'created_at']
    search_fields = ['name', 'description', 'team__name']
    readonly_fields = ['id', 'created_at']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['channel', 'sender', 'content_preview', 'parent_message', 'created_at']
    list_filter = ['channel', 'sender', 'created_at', 'is_edited']
    search_fields = ['content', 'sender__username', 'channel__name']
    readonly_fields = ['id', 'created_at', 'edited_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

class MeetingAttendanceInline(admin.TabularInline):
    model = MeetingAttendance
    extra = 0
    readonly_fields = ['created_at', 'duration_minutes']

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'organizer', 'team', 'start_time', 'attendee_count']
    list_filter = ['status', 'team', 'start_time']
    search_fields = ['title', 'description', 'organizer__username', 'team__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'start_time'
    inlines = [MeetingAttendanceInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time', 'timezone')
        }),
        ('Participants', {
            'fields': ('organizer', 'team')
        }),
        ('Integration', {
            'fields': ('zoom_meeting_id', 'meeting_url')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def attendee_count(self, obj):
        return obj.attendees.count()
    attendee_count.short_description = 'Attendees'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['id', 'created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_read=True, read_at=timezone.now())
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
    mark_as_unread.short_description = "Mark selected notifications as unread"

@admin.register(ActivityMetrics)
class ActivityMetricsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_work_minutes', 'productivity_score', 'tasks_completed']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date')
        }),
        ('Time Tracking', {
            'fields': ('total_work_minutes', 'active_minutes', 'idle_minutes')
        }),
        ('Productivity', {
            'fields': ('tasks_completed', 'tasks_started', 'meetings_attended', 'chat_messages_sent')
        }),
        ('Monitoring Data', {
            'fields': ('screenshots_taken', 'applications_used', 'websites_visited')
        }),
        ('Scores', {
            'fields': ('productivity_score', 'engagement_score', 'collaboration_score')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration_type', 'organization', 'is_active', 'last_sync']
    list_filter = ['integration_type', 'is_active', 'organization']
    search_fields = ['name', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_sync']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'organization')
        }),
        ('Configuration', {
            'fields': ('config', 'is_active')
        }),
        ('Security', {
            'fields': ('credentials',),
            'classes': ('collapse',),
            'description': 'Credentials are encrypted in production'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'last_sync'),
            'classes': ('collapse',)
        })
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'description_preview', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__username', 'description', 'resource_type']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'
    
    def has_add_permission(self, request):
        return False  # Audit logs should not be manually created
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified

# Customize admin site
admin.site.site_header = "Employee Tracker & Collaboration Admin"
admin.site.site_title = "Employee Tracker Admin"
admin.site.index_title = "Welcome to Employee Tracker Administration"
