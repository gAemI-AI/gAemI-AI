from django.urls import path
from .views import NotificationRuleListCreateView, NotificationRuleDestroyView

urlpatterns = [
    # GET, POST /api/v1/notifications/rules/
    path('rules/', NotificationRuleListCreateView.as_view(), name='rule-list-create'),
    
    # DELETE /api/v1/notifications/rules/{rule_id}/
    path('rules/<int:rule_id>/', NotificationRuleDestroyView.as_view(), name='rule-delete'),
]