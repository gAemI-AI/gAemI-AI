from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = 'users'

urlpatterns = [
    # ============ 인증 관련 API ============
    # 회원가입
    path('register/', views.register, name='register'),
    
    # 로그인
    path('login/', views.login, name='login'),
    
    # 로그아웃
    path('logout/', views.logout, name='logout'),
    
    # ============ JWT 토큰 관련 API ============
    # 토큰 발급 (username + password로 access, refresh 토큰 획득)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 토큰 갱신 (refresh 토큰으로 새 access 토큰 획득)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ============ 사용자 정보 관련 API ============
    # 현재 로그인한 사용자 정보 조회
    path('me/', views.get_profile, name='profile'),
    
    # 사용자 정보 수정
    path('me/update/', views.update_profile, name='update_profile'),
    
    # 비밀번호 변경
    path('change-password/', views.change_password, name='change_password'),
]
