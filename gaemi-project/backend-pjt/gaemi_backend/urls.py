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
    path('api/chatbot/', include('chatbot.urls')), #  /api/chatbot/ask/ 로 요청
]