# 공식 이미지 사용 (3.5.1 + Python 3)
FROM apache/spark:3.5.1-python3

USER root

RUN apt-get update && \
    apt-get install -y curl python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/spark/requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /opt/spark/requirements.txt
# JAR 파일 경로
COPY jars /opt/spark/jars

WORKDIR /opt/spark/work-dir