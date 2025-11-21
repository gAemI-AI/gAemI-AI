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
    
    # 1. 인증(Auth) API (로그인, 로그아웃, 비번변경 등)
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    
    # 2. 회원가입 API
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),

    # 3. 주식 정보 API 연결 (...api/v1/stocks/로 시작하는 요청은 stock/urls.py로 보냄)
    path('api/v1/stocks/', include('stocks.urls')), 

    # 4. 관심 종목 API
    path('api/v1/watchlist/', include('watchlist.urls')),
]