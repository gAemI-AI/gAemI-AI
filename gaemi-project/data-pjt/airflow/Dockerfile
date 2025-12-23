# 공식 이미지 기반
FROM apache/airflow:2.7.1

# requirements.txt 복사
COPY requirements.txt /requirements.txt

# 라이브러리 설치 (airflow 유저 권한으로 설치됨)
RUN pip install --no-cache-dir -r /requirements.txt