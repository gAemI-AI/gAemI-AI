# WebSocket 실시간 데이터 연동 가이드

## 🎯 개요
- **프론트엔드**: WebSocket으로 백엔드에서 실시간 주식 데이터 및 알림 수신
- **백엔드**: Kafka에서 메시지를 받아 Django Channels를 통해 WebSocket으로 전송

## 📁 파일 구조

### 백엔드
```
backend-pjt/
├── notifications/
│   ├── consumers.py              # WebSocket consumers (이미 존재)
│   ├── kafka_bridge.py           # ✨ NEW: Kafka 구독 및 WebSocket 전송
│   ├── apps.py                   # ✨ MODIFIED: Kafka Bridge 초기화
│   └── management/commands/
│       └── send_websocket_test.py # ✨ NEW: 테스트 데이터 전송 명령어
└── gaemi_backend/
    ├── routing.py                # WebSocket 라우팅 (이미 존재)
    ├── asgi.py                   # ASGI 설정 (이미 존재)
    └── settings.py               # ✨ MODIFIED: KAFKA_BROKER 설정 추가
```

### 프론트엔드
```
frontend-pjt/src/
├── services/
│   └── websocketService.js       # ✨ NEW: WebSocket 서비스
├── components/dashboard/
│   └── StockDetailCard.vue       # ✨ MODIFIED: WebSocket 데이터 연동
└── pages/
    └── DashboardPage.vue         # ✨ MODIFIED: 알림 구독 추가
```

## 🚀 동작 흐름

```
Kafka Topic → Kafka Bridge (Backend) → Redis Channel Layer → WebSocket Consumer → Frontend (Browser)

┌─────────────────────────────┐
│     Kafka Topics            │
├─────────────────────────────┤
│ 1. alert                    │
│ 2. stock-ticks              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Kafka Bridge Service      │ (kafka_bridge.py)
│   - KafkaConsumer 스레드    │
│   - async_to_sync로 전송    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Redis Channel Layer        │
│  (Django Channels)          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   WebSocket Consumers       │ (consumers.py)
│   - NotificationConsumer    │
│   - ChartConsumer           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Frontend (Browser)        │
│   WebSocket 연결            │
│   - 실시간 차트 업데이트    │
│   - 알림 표시               │
└─────────────────────────────┘
```

## 📝 사용 방법

### 1️⃣ 백엔드 실행 (Docker)

```bash
cd gaemi-project
docker-compose up -d
```

이렇게 하면:
- ✅ Django 백엔드 실행
- ✅ Redis 실행 (Channel Layer용)
- ✅ Kafka 실행
- ✅ PostgreSQL 실행

### 2️⃣ 테스트 데이터 전송

```bash
# 컨테이너 내부에서 명령어 실행
docker-compose exec backend python manage.py send_websocket_test

# 특정 타입만 전송
docker-compose exec backend python manage.py send_websocket_test --type alert
docker-compose exec backend python manage.py send_websocket_test --type stock
```

### 3️⃣ 프론트엔드 실행

```bash
cd gaemi-project/frontend-pjt
npm run dev

# http://localhost:5173 접속
```

### 4️⃣ 실시간 데이터 확인

**브라우저 개발자 도구 콘솔에서:**
```javascript
// WebSocket 연결 확인
// [005930] WebSocket 연결 성공  // 종목코드
// [Notifications 1] WebSocket 연결 성공  // 사용자ID
```

**대시보드:**
- 📈 왼쪽: 검색한 종목의 실시간 차트 업데이트
- ⭐ 왼쪽: 관심종목의 실시간 차트 업데이트
- 🔔 우측: 실시간 알림 표시

## 🔧 커스터마이징

### Kafka 메시지 형식 변경

**Alert 메시지:**
```json
{
  "user_id": "1",
  "message": "삼성전자 목표가 도달!"
}
```

**Stock Tick 메시지:**
```json
{
  "code": "005930",
  "price": 76000,
  "rate": 2.5,
  "timestamp": 1709000000000
}
```

### WebSocket URL 변경

프론트엔드 (src/services/websocketService.js):
```javascript
const WS_BASE_URL = 'ws://localhost:8000';  // 이 부분 수정
```

### 로깅 레벨 조정

백엔드 (gaemi_backend/settings.py)에 추가:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # INFO, WARNING, ERROR로도 설정 가능
    },
}
```

## 🐛 트러블슈팅

### Q: WebSocket 연결이 실패합니다
**A:** 확인사항:
1. 백엔드 실행 여부: `docker-compose ps`
2. Redis 실행 여부: `docker-compose logs redis`
3. WebSocket URL 확인: `ws://localhost:8000`
4. CORS 설정 확인: `settings.py`의 ALLOWED_HOSTS

### Q: Kafka 메시지가 받아지지 않습니다
**A:** 확인사항:
1. Kafka 실행: `docker-compose logs kafka`
2. 토픽 생성 확인: `docker-compose exec kafka kafka-topics --list --bootstrap-server kafka:9092`
3. 메시지 전송 시도: `python manage.py send_websocket_test`

### Q: 데이터가 수신되지만 화면에 업데이트 안 됨
**A:** 확인사항:
1. 종목코드 확인 (검색 후 선택했는지)
2. 브라우저 콘솔에서 WebSocket 메시지 확인
3. 프론트엔드 콘솔에 에러 메시지가 있는지 확인

### Q: "Kafka Bridge 초기화 실패" 에러
**A:**
1. Django가 정상 실행 중인지 확인
2. Kafka 서비스가 실행 중인지 확인
3. logs 확인: `docker-compose logs backend | grep -i kafka`

## 📊 모니터링

### 로그 확인

```bash
# 백엔드 로그
docker-compose logs -f backend

# Kafka 로그
docker-compose logs -f kafka

# Redis 로그
docker-compose logs -f redis

# 모든 로그
docker-compose logs -f
```

### Kafka 토픽 모니터링

```bash
# 토픽 목록 확인
docker-compose exec kafka kafka-topics --list --bootstrap-server kafka:9092

# alert 토픽 구독
docker-compose exec kafka kafka-console-consumer --topic alert --bootstrap-server kafka:9092 --from-beginning

# stock-ticks 토픽 구독
docker-compose exec kafka kafka-console-consumer --topic stock-ticks --bootstrap-server kafka:9092 --from-beginning
```

## ✨ 다음 단계

1. **실시간 데이터 연동**: 실제 데이터 producer와 연동
2. **차트 라이브러리**: Chart.js, ECharts 등으로 더 예쁜 차트 구현
3. **거래량 표시**: WebSocket에서 거래량 데이터 추가 수신
4. **알림 스타일**: Toast, 사운드 등으로 알림 UI 개선
5. **에러 처리**: WebSocket 재연결, 타임아웃 등 처리 강화
