# 🔧 문제 해결 가이드

## 1️⃣ Market Index가 빈 배열 반환되는 문제

### 원인 분석
- Elasticsearch의 `index-ticks` 인덱스에 데이터가 없음
- 가능한 원인들:
  1. Producer가 WebSocket에서 지수 데이터를 받지 못함
  2. Kafka 토픽 `index-ticks`에 데이터가 없음
  3. Consumer가 Kafka 데이터를 처리하지 못함
  4. ES 인덱스 매핑 문제

### 진단 방법

**1️⃣ Docker 로그 확인**
```bash
# Producer 로그 확인
docker logs gaemi_producer_stock | grep -i "index\|지수"

# Consumer 로그 확인
docker logs gaemi_consumer_index | tail -50

# Elasticsearch 로그 확인
docker logs gaemi_elasticsearch | tail -50
```

**2️⃣ Kafka 토픽 데이터 확인**
```bash
# Kafka 컨테이너 진입
docker exec -it gaemi_kafka bash

# index-ticks 토픽 데이터 확인
kafka-console-consumer.sh \
  --bootstrap-servers localhost:9092 \
  --topic index-ticks \
  --from-beginning \
  --max-messages 5
```

**3️⃣ Elasticsearch 상태 확인**
```bash
# ES 인덱스 목록
curl http://localhost:9200/_cat/indices

# index-ticks 인덱스 상태
curl http://localhost:9200/index-ticks/_count

# 인덱스 매핑 확인
curl http://localhost:9200/index-ticks/_mapping
```

### 빠른 해결 방법

**Option A: 전체 재시작 (권장)**
```bash
docker-compose down
docker-compose up -d
```

**Option B: 문제 서비스만 재시작**
```bash
# 1. Consumer 재시작
docker restart gaemi_consumer_index

# 2. Producer 재시작  
docker restart gaemi_producer_stock

# 3. ES 재시작
docker restart gaemi_elasticsearch
```

**Option C: 인덱스 재생성**
```bash
# ES 인덱스 삭제
curl -X DELETE http://localhost:9200/index-ticks

# Consumer 재시작 (인덱스 자동 생성)
docker restart gaemi_consumer_index
```

---

## 2️⃣ Weekly Reports 404 오류 (✅ 해결됨)

### 해결 방법
- `WeeklyReportView` 클래스 추가
- `stocks/urls.py`에 경로 등록
- 프론트엔드 URL 수정: `/api/v1/stocks/reports/weekly/`

### 테스트 방법
```bash
# 로그인 후 테스트 (Authorization 헤더 필수)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/stocks/reports/weekly/
```

---

## 3️⃣ 주간 리포트가 표시되지 않는 경우

### 원인
- DB의 `weekly_reports` 테이블에 데이터가 없음
- Spark Job이 실행되지 않았음

### 해결 방법
```bash
# Spark Job 수동 실행
docker exec gaemi_spark_master bash -c \
  "spark-submit /opt/spark/jobs/weekly_report_job.py"

# 또는 스케줄링된 시간 대기 (일반적으로 매주 토요일 밤)
```

---

## 📊 전체 데이터 흐름 확인

```
KIS WebSocket (종목/지수)
    ↓
Producer (producer-stock)
    ↓
Kafka Topics:
  - stock-ticks (체결가)
  - stock-orderbook (호가)
  - index-ticks (지수) ← Market Index 사용
    ↓
Consumer & Flink Jobs
    ↓
Elasticsearch & PostgreSQL
    ↓
Backend API (/api/v1/stocks/...)
    ↓
Frontend (Vue)
```

---

## 🛠️ 환경 변수 확인

### 필수 환경 변수
```
# docker-compose.yml에서 확인:
POSTGRES_DB=gaemi_ai
POSTGRES_USER=gaemi
POSTGRES_PASSWORD=gaemigaemi11
POSTGRES_HOST=db
REDIS_HOST=redis

# 데이터 파이프라인:
KAFKA_BROKER=kafka:29092
TOPIC_NAME=index-ticks (for consumer-index)
ES_HOST=http://elasticsearch:9200
ES_INDEX=index-ticks
```

---

## 📞 문제 해결 체크리스트

- [ ] Docker 컨테이너 모두 실행 중 (`docker ps`)
- [ ] Kafka 토픽 생성됨 (`kafka-topics.sh --list`)
- [ ] Elasticsearch 응답 정상 (`curl http://localhost:9200`)
- [ ] 백엔드 API 응답 정상 (`curl http://localhost:8000/api/v1/stocks/`)
- [ ] WebSocket 연결 정상 (Producer 로그 확인)
- [ ] Consumer 데이터 처리 중 (Consumer 로그 확인)
