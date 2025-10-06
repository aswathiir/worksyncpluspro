"""
API views for collaboration features
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Organization, Team, TeamMembership, Task, TaskTimeEntry,
    ChatChannel, ChatMessage, Meeting, MeetingAttendance,
    Notification, ActivityMetrics, Integration
)
from .serializers import (
    OrganizationSerializer, TeamSerializer, TaskSerializer, TaskTimeEntrySerializer,
    ChatChannelSerializer, ChatMessageSerializer, MeetingSerializer,
    NotificationSerializer, ActivityMetricsSerializer, IntegrationSerializer
)

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def dashboard_stats(self, request, pk=None):
        """Get dashboard statistics for an organization"""
        org = self.get_object()
        
        # Get date range (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        stats = {
            'teams': org.teams.count(),
            'total_members': sum(team.members.count() for team in org.teams.all()),
            'active_tasks': Task.objects.filter(
                team__organization=org,
                status__in=['todo', 'in_progress']
            ).count(),
            'completed_tasks_30d': Task.objects.filter(
                team__organization=org,
                status='done',
                completed_at__date__gte=start_date
            ).count(),
            'meetings_30d': Meeting.objects.filter(
                team__organization=org,
                start_time__date__gte=start_date
            ).count(),
            'avg_productivity_score': ActivityMetrics.objects.filter(
                user__teams__organization=org,
                date__gte=start_date
            ).aggregate(avg_score=Avg('productivity_score'))['avg_score'] or 0
        }
        
        return Response(stats)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter teams based on user membership"""
        user = self.request.user
        if user.is_staff:
            return Team.objects.all()
        return Team.objects.filter(members=user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            membership, created = TeamMembership.objects.get_or_create(
                user=user,
                team=team,
                defaults={'role': role}
            )
            
            if not created:
                return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Member added successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def activity_summary(self, request, pk=None):
        """Get team activity summary"""
        team = self.get_object()
        
        # Get date range
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        summary = {
            'task_completion_rate': self._get_task_completion_rate(team, start_date, end_date),
            'avg_productivity': self._get_avg_productivity(team, start_date, end_date),
            'meeting_attendance': self._get_meeting_attendance(team, start_date, end_date),
            'chat_activity': self._get_chat_activity(team, start_date, end_date)
        }
        
        return Response(summary)
    
    def _get_task_completion_rate(self, team, start_date, end_date):
        total_tasks = Task.objects.filter(team=team, created_at__date__gte=start_date).count()
        completed_tasks = Task.objects.filter(
            team=team, 
            status='done',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).count()
        return (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    def _get_avg_productivity(self, team, start_date, end_date):
        return ActivityMetrics.objects.filter(
            user__teams=team,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(avg_score=Avg('productivity_score'))['avg_score'] or 0
    
    def _get_meeting_attendance(self, team, start_date, end_date):
        meetings = Meeting.objects.filter(
            team=team,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )
        if not meetings.exists():
            return 0
        
        total_invites = sum(meeting.attendees.count() for meeting in meetings)
        total_attended = MeetingAttendance.objects.filter(
            meeting__in=meetings,
            status='attended'
        ).count()
        
        return (total_attended / total_invites * 100) if total_invites > 0 else 0
    
    def _get_chat_activity(self, team, start_date, end_date):
        return ChatMessage.objects.filter(
            channel__team=team,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tasks based on user access"""
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(
            Q(assignee=user) | Q(reporter=user) | Q(team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def start_work(self, request, pk=None):
        """Start working on a task"""
        task = self.get_object()
        
        # Create time entry
        time_entry = TaskTimeEntry.objects.create(
            task=task,
            user=request.user,
            start_time=timezone.now()
        )
        
        # Update task status if needed
        if task.status == 'todo':
            task.status = 'in_progress'
            task.save()
        
        return Response({'message': 'Work started', 'time_entry_id': time_entry.id})
    
    @action(detail=True, methods=['post'])
    def stop_work(self, request, pk=None):
        """Stop working on a task"""
        task = self.get_object()
        time_entry_id = request.data.get('time_entry_id')
        
        try:
            time_entry = TaskTimeEntry.objects.get(
                id=time_entry_id,
                task=task,
                user=request.user,
                end_time__isnull=True
            )
            
            time_entry.end_time = timezone.now()
            time_entry.duration_minutes = int(
                (time_entry.end_time - time_entry.start_time).total_seconds() / 60
            )
            time_entry.save()
            
            # Update task actual hours
            task.actual_hours += time_entry.duration_minutes / 60
            task.save()
            
            return Response({'message': 'Work stopped', 'duration_minutes': time_entry.duration_minutes})
        except TaskTimeEntry.DoesNotExist:
            return Response({'error': 'Time entry not found'}, status=status.HTTP_404_NOT_FOUND)

class ChatChannelViewSet(viewsets.ModelViewSet):
    queryset = ChatChannel.objects.all()
    serializer_class = ChatChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter channels based on user membership"""
        user = self.request.user
        return ChatChannel.objects.filter(members=user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a channel"""
        channel = self.get_object()
        messages = ChatMessage.objects.filter(
            channel=channel,
            parent_message__isnull=True  # Only top-level messages
        ).order_by('-created_at')
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        messages = messages[start:end]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to the channel"""
        channel = self.get_object()
        content = request.data.get('content')
        parent_id = request.data.get('parent_id')
        
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message_data = {
            'channel': channel,
            'sender': request.user,
            'content': content
        }
        
        if parent_id:
            try:
                parent_message = ChatMessage.objects.get(id=parent_id, channel=channel)
                message_data['parent_message'] = parent_message
            except ChatMessage.DoesNotExist:
                return Response({'error': 'Parent message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        message = ChatMessage.objects.create(**message_data)
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter meetings based on user participation"""
        user = self.request.user
        if user.is_staff:
            return Meeting.objects.all()
        return Meeting.objects.filter(
            Q(organizer=user) | Q(attendees=user) | Q(team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def join_meeting(self, request, pk=None):
        """Mark user as joined to meeting"""
        meeting = self.get_object()
        
        attendance, created = MeetingAttendance.objects.get_or_create(
            meeting=meeting,
            user=request.user,
            defaults={'status': 'attended', 'joined_at': timezone.now()}
        )
        
        if not created and not attendance.joined_at:
            attendance.joined_at = timezone.now()
            attendance.status = 'attended'
            attendance.save()
        
        return Response({'message': 'Joined meeting successfully'})

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the current user"""
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'message': 'All notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        if not notification.is_read:
            notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})

    @action(detail=True, methods=['post'])
    def accept_invitation(self, request, pk=None):
        """Accept a project invitation from notification"""
        notification = self.get_object()

        if notification.notification_type != 'project_invitation':
            return Response({'error': 'This notification is not a project invitation'}, status=status.HTTP_400_BAD_REQUEST)

        if not notification.invitation_token:
            return Response({'error': 'No invitation token found'}, status=status.HTTP_400_BAD_REQUEST)

        invitation_token = notification.invitation_token

        # Check if invitation is still valid
        if invitation_token.accepted:
            return Response({'error': 'Invitation has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        # Accept the invitation
        invitation_token.accepted = True
        invitation_token.save()

        # Add user to project
        project = invitation_token.project
        project.members.add(invitation_token.new_member)

        # Mark notification as read
        notification.mark_as_read()

        # Create a success notification for the manager
        from django.contrib.auth import get_user_model
        User = get_user_model()

        success_notification = Notification.objects.create(
            recipient=invitation_token.manager,
            notification_type='system',
            title='Project Invitation Accepted',
            message=f'{invitation_token.new_member.username} has accepted the invitation to join {project.name}.',
            project=project,
            data={'accepted_by': invitation_token.new_member.username}
        )

        return Response({
            'message': f'You have successfully joined {project.name}',
            'project_id': project.id,
            'project_name': project.name
        })

class ActivityMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityMetrics.objects.all()
    serializer_class = ActivityMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter metrics based on user access"""
        user = self.request.user
        if user.is_staff:
            return ActivityMetrics.objects.all()
        return ActivityMetrics.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """Get dashboard data for current user"""
        user = request.user
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = ActivityMetrics.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Aggregate data
        total_work_time = sum(m.total_work_minutes for m in metrics)
        avg_productivity = metrics.aggregate(avg=Avg('productivity_score'))['avg'] or 0
        total_tasks_completed = sum(m.tasks_completed for m in metrics)
        
        # Daily breakdown
        daily_data = []
        for metric in metrics:
            daily_data.append({
                'date': metric.date,
                'work_minutes': metric.total_work_minutes,
                'productivity_score': metric.productivity_score,
                'tasks_completed': metric.tasks_completed
            })
        
        return Response({
            'summary': {
                'total_work_hours': total_work_time / 60,
                'avg_productivity_score': avg_productivity,
                'total_tasks_completed': total_tasks_completed,
                'days_tracked': len(daily_data)
            },
            'daily_data': daily_data
        })
