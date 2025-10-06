"""
URL configuration for collaboration API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'chat-channels', views.ChatChannelViewSet)
router.register(r'meetings', views.MeetingViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'activity-metrics', views.ActivityMetricsViewSet)

urlpatterns = [
    path('api/collaboration/', include(router.urls)),
]
