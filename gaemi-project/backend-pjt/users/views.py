from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User
from .serializers import UserSerializer


# ========== 회원가입 API ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/v1/users/register/
    회원가입 요청
    
    Request Body:
    {
        "username": "user123",
        "email": "user@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "nickname": "닉네임" (선택)
    }
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        nickname = request.data.get('nickname', '')

        # 필수 필드 확인
        if not all([username, email, password, password_confirm]):
            return Response(
                {'error': '필수 필드를 모두 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 비밀번호 일치 확인
        if password != password_confirm:
            return Response(
                {'error': '비밀번호가 일치하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 비밀번호 강도 검사
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 중복 확인
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': '이미 사용 중인 사용자명입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': '이미 사용 중인 이메일입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 사용자 생성
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            nickname=nickname if nickname else username
        )

        # 토큰 생성
        refresh = RefreshToken.for_user(user)
        
        return Response(
            {
                'message': '회원가입이 완료되었습니다.',
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== 로그인 API ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/v1/users/login/
    로그인 요청
    
    Request Body:
    {
        "username": "user123",
        "password": "password123"
    }
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': '사용자명과 비밀번호를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 사용자 인증
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': '잘못된 사용자명 또는 비밀번호입니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 토큰 생성
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': '로그인 성공',
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== 로그아웃 API ==========
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    POST /api/v1/users/logout/
    로그아웃 요청 (프론트에서 토큰 삭제)
    """
    return Response(
        {'message': '로그아웃 되었습니다.'},
        status=status.HTTP_200_OK
    )


# ========== 현재 사용자 정보 조회 ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    GET /api/v1/users/me/
    현재 로그인한 사용자 정보 조회
    """
    user = request.user
    return Response(
        UserSerializer(user).data,
        status=status.HTTP_200_OK
    )


# ========== 사용자 정보 수정 ==========
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    PUT/PATCH /api/v1/users/me/
    사용자 정보 수정 (nickname, profile_image 등)
    
    Request Body:
    {
        "nickname": "새로운닉네임",
        "profile_image": "https://example.com/image.jpg",
        "first_name": "홍",
        "last_name": "길동"
    }
    """
    user = request.user
    
    # 수정 가능한 필드들
    if 'nickname' in request.data:
        user.nickname = request.data['nickname']
    if 'profile_image' in request.data:
        user.profile_image = request.data['profile_image']
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    
    user.save()
    
    return Response(
        {
            'message': '사용자 정보가 수정되었습니다.',
            'user': UserSerializer(user).data
        },
        status=status.HTTP_200_OK
    )


# ========== 비밀번호 변경 ==========
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    POST /api/v1/users/change-password/
    비밀번호 변경
    
    Request Body:
    {
        "old_password": "현재비밀번호",
        "new_password": "새로운비밀번호",
        "new_password_confirm": "새로운비밀번호"
    }
    """
    try:
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if not all([old_password, new_password, new_password_confirm]):
            return Response(
                {'error': '필수 필드를 모두 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 기존 비밀번호 확인
        if not user.check_password(old_password):
            return Response(
                {'error': '기존 비밀번호가 일치하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 새 비밀번호 일치 확인
        if new_password != new_password_confirm:
            return Response(
                {'error': '새 비밀번호가 일치하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 비밀번호 강도 검사
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        return Response(
            {'message': '비밀번호가 변경되었습니다.'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )