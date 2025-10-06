"""
Management command to set up sample collaboration data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from collaboration.models import (
    Organization, Team, TeamMembership, Task, TaskTimeEntry,
    ChatChannel, ChatMessage, Meeting, MeetingAttendance,
    Notification, ActivityMetrics
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up sample collaboration data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all collaboration data before creating new data',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting collaboration data...')
            self.reset_data()
        
        self.stdout.write('Creating sample collaboration data...')
        
        # Create organization
        org = self.create_organization()
        
        # Create users
        users = self.create_users()
        
        # Create teams
        teams = self.create_teams(org, users)
        
        # Create tasks
        tasks = self.create_tasks(teams, users)
        
        # Create chat channels and messages
        self.create_chat_data(teams, users)
        
        # Create meetings
        self.create_meetings(teams, users)
        
        # Create activity metrics
        self.create_activity_metrics(users)
        
        # Create notifications
        self.create_notifications(users, tasks)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample collaboration data!')
        )
    
    def reset_data(self):
        """Reset all collaboration data"""
        models_to_reset = [
            ActivityMetrics, Notification, MeetingAttendance, Meeting,
            ChatMessage, ChatChannel, TaskTimeEntry, Task,
            TeamMembership, Team, Organization
        ]
        
        for model in models_to_reset:
            model.objects.all().delete()
    
    def create_organization(self):
        """Create sample organization"""
        org, created = Organization.objects.get_or_create(
            name='TechCorp Solutions',
            defaults={
                'description': 'A leading technology solutions company focused on innovation and collaboration.'
            }
        )
        if created:
            self.stdout.write(f'Created organization: {org.name}')
        return org
    
    def create_users(self):
        """Create sample users"""
        users_data = [
            {'username': 'john_doe', 'email': 'john@techcorp.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@techcorp.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_johnson', 'email': 'mike@techcorp.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
            {'username': 'sarah_wilson', 'email': 'sarah@techcorp.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
            {'username': 'david_brown', 'email': 'david@techcorp.com', 'first_name': 'David', 'last_name': 'Brown'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            users.append(user)
        
        return users
    
    def create_teams(self, org, users):
        """Create sample teams"""
        teams_data = [
            {'name': 'Development Team', 'description': 'Frontend and backend developers', 'lead': users[0]},
            {'name': 'Design Team', 'description': 'UI/UX designers and creative team', 'lead': users[1]},
            {'name': 'QA Team', 'description': 'Quality assurance and testing team', 'lead': users[2]},
        ]
        
        teams = []
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                organization=org,
                defaults={
                    'description': team_data['description'],
                    'lead': team_data['lead']
                }
            )
            
            if created:
                # Add team members
                team_users = random.sample(users, random.randint(2, 4))
                for user in team_users:
                    role = 'lead' if user == team_data['lead'] else 'member'
                    TeamMembership.objects.get_or_create(
                        user=user,
                        team=team,
                        defaults={'role': role}
                    )
                
                self.stdout.write(f'Created team: {team.name} with {len(team_users)} members')
            
            teams.append(team)
        
        return teams
    
    def create_tasks(self, teams, users):
        """Create sample tasks"""
        task_titles = [
            'Implement user authentication system',
            'Design new dashboard layout',
            'Fix login page responsiveness',
            'Create API documentation',
            'Set up automated testing',
            'Optimize database queries',
            'Design mobile app wireframes',
            'Implement real-time notifications',
            'Create user onboarding flow',
            'Fix security vulnerabilities'
        ]
        
        tasks = []
        for i, title in enumerate(task_titles):
            team = random.choice(teams)
            assignee = random.choice(list(team.members.all()))
            reporter = random.choice(users)
            
            task = Task.objects.create(
                title=title,
                description=f'Detailed description for {title.lower()}',
                status=random.choice(['todo', 'in_progress', 'review', 'done']),
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                assignee=assignee,
                reporter=reporter,
                team=team,
                estimated_hours=random.randint(2, 20),
                actual_hours=random.randint(0, 15),
                due_date=timezone.now() + timedelta(days=random.randint(1, 30))
            )
            
            # Create some time entries
            if random.choice([True, False]):
                TaskTimeEntry.objects.create(
                    task=task,
                    user=assignee,
                    start_time=timezone.now() - timedelta(hours=random.randint(1, 8)),
                    end_time=timezone.now() - timedelta(hours=random.randint(0, 2)),
                    duration_minutes=random.randint(30, 240),
                    activity_score=random.uniform(0.6, 1.0),
                    screenshot_count=random.randint(5, 25)
                )
            
            tasks.append(task)
        
        self.stdout.write(f'Created {len(tasks)} tasks')
        return tasks
    
    def create_chat_data(self, teams, users):
        """Create sample chat channels and messages"""
        for team in teams:
            # Create team channel
            channel = ChatChannel.objects.create(
                name=f'{team.name.lower().replace(" ", "-")}',
                description=f'General discussion for {team.name}',
                channel_type='team',
                team=team
            )
            
            # Add team members to channel
            channel.members.set(team.members.all())
            
            # Create sample messages
            for i in range(random.randint(10, 25)):
                sender = random.choice(list(team.members.all()))
                ChatMessage.objects.create(
                    channel=channel,
                    sender=sender,
                    content=f'Sample message {i+1} from {sender.first_name}',
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )
        
        # Create general channel
        general_channel = ChatChannel.objects.create(
            name='general',
            description='General company discussion',
            channel_type='general'
        )
        general_channel.members.set(users)
        
        self.stdout.write(f'Created {len(teams) + 1} chat channels with messages')
    
    def create_meetings(self, teams, users):
        """Create sample meetings"""
        meeting_titles = [
            'Weekly Team Standup',
            'Sprint Planning Meeting',
            'Design Review Session',
            'Client Presentation',
            'Code Review Meeting'
        ]
        
        for i, title in enumerate(meeting_titles):
            team = random.choice(teams)
            organizer = team.lead or random.choice(list(team.members.all()))
            
            start_time = timezone.now() + timedelta(days=random.randint(-7, 14))
            meeting = Meeting.objects.create(
                title=title,
                description=f'Description for {title}',
                status=random.choice(['scheduled', 'completed']),
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                organizer=organizer,
                team=team
            )
            
            # Add attendees
            attendees = random.sample(list(team.members.all()), random.randint(2, team.members.count()))
            for attendee in attendees:
                MeetingAttendance.objects.create(
                    meeting=meeting,
                    user=attendee,
                    status=random.choice(['invited', 'accepted', 'attended']),
                    engagement_score=random.uniform(0.5, 1.0),
                    attention_score=random.uniform(0.6, 1.0)
                )
        
        self.stdout.write(f'Created {len(meeting_titles)} meetings')
    
    def create_activity_metrics(self, users):
        """Create sample activity metrics"""
        for user in users:
            for days_ago in range(30):  # Last 30 days
                date = timezone.now().date() - timedelta(days=days_ago)
                
                ActivityMetrics.objects.get_or_create(
                    user=user,
                    date=date,
                    defaults={
                        'total_work_minutes': random.randint(300, 480),  # 5-8 hours
                        'active_minutes': random.randint(250, 400),
                        'idle_minutes': random.randint(50, 100),
                        'tasks_completed': random.randint(0, 3),
                        'tasks_started': random.randint(0, 2),
                        'meetings_attended': random.randint(0, 3),
                        'chat_messages_sent': random.randint(5, 25),
                        'screenshots_taken': random.randint(20, 60),
                        'applications_used': ['VS Code', 'Chrome', 'Slack', 'Figma'],
                        'websites_visited': ['github.com', 'stackoverflow.com', 'docs.python.org'],
                        'productivity_score': random.uniform(0.6, 1.0),
                        'engagement_score': random.uniform(0.5, 1.0),
                        'collaboration_score': random.uniform(0.7, 1.0)
                    }
                )
        
        self.stdout.write(f'Created activity metrics for {len(users)} users over 30 days')
    
    def create_notifications(self, users, tasks):
        """Create sample notifications"""
        notification_types = [
            ('task_assigned', 'New Task Assigned'),
            ('task_completed', 'Task Completed'),
            ('meeting_reminder', 'Meeting Reminder'),
            ('chat_mention', 'You were mentioned in chat'),
            ('system', 'System Update Available')
        ]
        
        for user in users:
            for i in range(random.randint(3, 8)):
                notif_type, title = random.choice(notification_types)
                
                Notification.objects.create(
                    recipient=user,
                    notification_type=notif_type,
                    title=title,
                    message=f'Sample notification message for {user.first_name}',
                    is_read=random.choice([True, False]),
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 48))
                )
        
        self.stdout.write(f'Created notifications for {len(users)} users')
