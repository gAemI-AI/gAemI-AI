from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    직접 로그인 방식의 커스텀 User 모델
    기본 AbstractUser(username, email, password, first_name, last_name)는 그대로 사용
    """

    # 1. 닉네임 (선택사항)
    nickname = models.CharField(max_length=50, null=True, blank=True, unique=True)

    # 2. 프로필 이미지 (선택사항)
    profile_image = models.URLField(max_length=500, null=True, blank=True)
    
    # 3. 계정 생성일
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.email})"