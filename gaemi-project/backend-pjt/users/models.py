from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    소셜 로그인을 고려한 모델 설계
    기본 AbstractUser(username, email, password)는 그대로 사용
    """

    # 1. 닉네임 (소셜에서 받아오는 이름)
    nickname = models.CharField(max_length=10, null=True, blank=True)

    # 2. 프로필 이미지 (URL)
    profile_image = models.URLField(max_length=500, null=True, blank=True)

    # 3. 소셜 로그인 제공자 (kakao, google, naver) -> 추후 확장 가능

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username