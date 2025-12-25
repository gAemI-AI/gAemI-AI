from django.urls import path
from .views import NotificationRuleListCreateView, NotificationRuleUpdateDestroyView

urlpatterns = [
    # GET, POST /api/v1/notifications/rules/
    path('rules/', NotificationRuleListCreateView.as_view(), name='rule-list-create'),
    
    # GET, PATCH, DELETE /api/v1/notifications/rules/{rule_id}/
    path('rules/<int:rule_id>/', NotificationRuleUpdateDestroyView.as_view(), name='rule-update-destroy'),
]