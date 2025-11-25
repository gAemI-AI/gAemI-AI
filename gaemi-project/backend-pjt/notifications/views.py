# perfom_create(작성자 자동 지정)와 get_queryset(내것만 보기)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import NotificationRule
from .serializers import NotificationRuleSerializer

# 1. 알림 규칙 조회(GET) 및 생성(POST)

class NotificationRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]

    # 내 규칙만 가져오기
    def get_queryset(self):
        return NotificationRule.objects.filter(user=self.request.user)
    
    # 저장할 때 내 아이디로 저장하기
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
# 2. 알림 규칙 삭제(Delete) - rule_id 기준
class NotificationRuleDestroyView(generics.DestroyAPIView):
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'rule_id' # URL에서 rule_id 찾음

    def get_queryset(self):
        return NotificationRule.objects.filter(user=self.request.user)