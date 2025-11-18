# backend-pjt/Dockerfile

# 1. 베이스 이미지
FROM python:3.10

# 2. 환경 변수 설정: 파이썬 로그 바로 출력되도록 정의
ENV PYTHONBUFFERED=1

# 3. 작업 디렉토리 설정: 컨테이너 내부의 /app 폴더에서 작업
WORKDIR /app

# 4. 라이브러리 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. 코드 복사: backend-pjt의 모든 파일을 컨테이너의 /app 폴더로 복사
COPY . .

# 6. 기본 실행 명령어
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]