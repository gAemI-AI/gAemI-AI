"""
URL configuration for gaemi_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

# 🌟 Swagger 관련 임포트
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 🌟 Swagger 정보 설정
schema_view = get_schema_view(
   openapi.Info(
      title="gAemI-AI API",
      default_version='v1',
      description="gAemi-AI 프로젝트 API 명세서입니다.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@gaemi.ai"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. 인증 및 사용자 API (로그인, 회원가입, 프로필, 비밀번호 변경 등)
    path('api/v1/users/', include('users.urls')),

    # 2. 주식 정보 API 연결 (...api/v1/stocks/로 시작하는 요청은 stocks/urls.py로 보냄)
    path('api/v1/stocks/', include('stocks.urls')), 

    # 3. 관심 종목 API
    path('api/v1/watchlist/', include('watchlist.urls')),
    
    # 4. 알림 API 연결
    path('api/v1/notifications/', include('notifications.urls')),

    # 5. chatbot 연결
    path('api/v1/chatbot/', include('chatbot.urls')), #  /api/chatbot/ask/ 로 요청

    # ------------- Swagger URL 연결 ------------- #
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # ------------------------------------------ #

    # 6. news 앱 연결
    path('api/v1/news/', include('news.urls')),
]