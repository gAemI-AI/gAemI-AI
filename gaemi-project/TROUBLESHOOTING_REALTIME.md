# 🔧 대시보드 차트 실시간 데이터 - 트러블슈팅 가이드

## 상황별 진단 및 해결책

---

## 🚨 증상 1: "차트는 보이는데 가격이 안 변해요"

### 가능한 원인들

#### ❌ 원인 1-1: WebSocket 연결 실패

**확인 방법**:
```javascript
// 브라우저 DevTools Console (F12 → Console 탭)에서
// 다음 메시지를 찾아보세요:

// ✅ 성공한 경우:
// "[005930] WebSocket 연결 성공"
// "[WebSocket 005930] 메시지 수신: {type: 'chart_update', data: {...}}"

// ❌ 실패한 경우:
// "[005930] WebSocket 에러: (에러 메시지)"
// 또는 아무 메시지도 없음
```

**해결책**:
```bash
# 1. Django 서버 상태 확인
docker ps | grep backend

# 2. Django 로그에서 에러 찾기
docker logs backend | grep -E "error|Error|ERROR|WebSocket"

# 3. WebSocket 엔드포인트가 정확한지 확인
# 현재: ws://localhost:8000/ws/stocks/{code}/
# ⚠️  Docker 네트워크 내부에서는 localhost가 아닐 수 있음
```

**해결 방법**:
```javascript
// frontend-pjt/src/services/websocketService.js에서
// 다음을 확인하세요:

const WS_BASE_URL = 'ws://localhost:8000';
// 또는 환경 변수로 설정
const WS_BASE_URL = process.env.VUE_APP_WS_URL || 'ws://localhost:8000';
```

---

#### ❌ 원인 1-2: Kafka 브리지가 시작되지 않음

**확인 방법**:
```bash
# Django 로그에서 다음 메시지를 찾으세요:
docker logs backend | grep "Stock Ticks Consumer"

# 예상 로그:
# "✅ Stock Ticks Consumer 시작"
# "🔄 Kafka Bridge 모든 컨슈머 시작됨"
```

**원인**:
- Kafka 컨테이너가 실행 중이지 않음
- Django 시작 시 Kafka Bridge 초기화 코드가 실행되지 않음

**해결책**:
```python
# backend-pjt/gaemi_backend/asgi.py에서
# Kafka Bridge 초기화 코드 확인

from notifications.kafka_bridge import kafka_bridge

# Django 시작 시 Kafka Bridge 시작
# (보통 apps.py 또는 ready() 메서드에서)
```

```python
# backend-pjt/notifications/apps.py 또는 manage.py에서

from notifications.kafka_bridge import kafka_bridge

# Django 앱 초기화 시
kafka_bridge.start_all_consumers()
```

---

#### ❌ 원인 1-3: Kafka가 `stock-ticks` 토픽에 데이터를 발행하지 않음

**확인 방법**:
```bash
# 1. Kafka 토픽 확인
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# 2. stock-ticks 토픽에 메시지가 있는지 확인
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --from-beginning \
  --max-messages 5

# 3. Producer 로그 확인
docker logs producer-stock | tail -50
```

**해결책**:
```bash
# Producer 재시작
docker restart producer-stock

# 또는 수동으로 테스트 메시지 발행
docker exec kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic stock-ticks
# 아래를 입력:
# {"code": "005930", "price": 76000, "rate": 2.5, "timestamp": 1703424600000}
```

---

### 🔍 단계별 진단 플로우

```
차트 가격이 안 변함
    ↓
┌─ (1) DevTools Console 확인 ─────┐
│                                  │
├─ WebSocket 연결 로그? ─────┐     │
│  ✅ 있음 → (2번으로)        │     │
│  ❌ 없음 → WS 연결 재확인   │     │
│          frontend config 확인  │
│          Django ASGI 설정 확인  │
│                              │
└──────────────────────────────┘

┌─ (2) Django 로그 확인 ──────────┐
│                                  │
├─ "Stock Ticks Consumer"? ──┐    │
│  ✅ 있음 → (3번으로)        │    │
│  ❌ 없음 → Kafka 연결 실패   │
│          docker-compose 확인  │
│          KAFKA_BROKER 설정 확인 │
│                             │
└─────────────────────────────┘

┌─ (3) Kafka 토픽 확인 ──────────┐
│                                 │
├─ stock-ticks에 메시지? ────┐   │
│  ✅ 있음 → WebSocket까지 추적 │   │
│  ❌ 없음 → Producer 확인    │   │
│         하단의 "원인 1-3" 참고  │
│                            │
└─────────────────────────────┘

┌─ (4) WebSocket 메시지 추적 ─┐
│                              │
├─ 브라우저 DevTools          │
│  Network 탭 → WS 필터       │
│  → Messages 탭에서           │
│    메시지가 오는지 확인      │
│                             │
│  ✅ 메시지 옴 → 프론트 로직 확인
│  ❌ 메시지 안 옴 → Django로 이동
│                             │
└──────────────────────────────┘
```

---

## 🚨 증상 2: "Elasticsearch에는 데이터가 있는데 차트가 안 나와요"

### 진단

```bash
# 1. Elasticsearch 상태 확인
curl http://localhost:9200/

# 2. raw-stocks 인덱스 조회
curl http://localhost:9200/raw-stocks/_search?size=1

# 3. 응답에서 데이터 구조 확인
# 예상: { "hits": { "hits": [...] } }

# 4. StockChartView가 제대로 집계하는지 테스트
curl "http://localhost:8000/api/v1/stocks/005930/chart/?range=1d&interval=1m"
```

### 해결책

```python
# backend-pjt/stocks/views.py의 StockChartView에서

# 1. ES 연결 확인
self.es = Elasticsearch(
    hosts=[{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}]
)

# Docker 내부 통신용 호스트는 'elasticsearch'
# (localhost ❌, elasticsearch ✅)

# 2. 쿼리 디버깅
try:
    response = self.es.search(index="raw-stocks", body=query_body)
    print(f"ES Response: {response}")  # 로깅 추가
except Exception as e:
    print(f"Chart Error: {e}")
    return Response([], status=status.HTTP_200_OK)
```

---

## 🚨 증상 3: "로그에 아무것도 안 뜬다"

### 원인: Kafka Bridge 초기화 코드가 없음

**해결책**:

Django 앱이 시작될 때 Kafka Bridge를 초기화하는 코드가 필요합니다.

```python
# backend-pjt/notifications/apps.py

from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        """Django 앱 시작 시 Kafka Bridge 시작"""
        from notifications.kafka_bridge import kafka_bridge
        kafka_bridge.start_all_consumers()
        print("✅ Kafka Bridge 시작됨")
```

또는

```python
# backend-pjt/gaemi_backend/settings.py에서
# 앱 등록 후 custom 초기화

# 또는 manage.py 실행 시
# python manage.py shell_plus
# >>> from notifications.kafka_bridge import kafka_bridge
# >>> kafka_bridge.start_all_consumers()
```

---

## 🚨 증상 4: "Producer 데이터가 없어요"

### 확인

```bash
# Producer 상태 확인
docker ps | grep producer-stock

# Producer 로그 확인
docker logs producer-stock

# 데이터 소스 확인
# - API 연결 여부
# - 네트워크 설정
# - 시간대 설정 (현재 시간이 주식 거래 시간인가?)
```

### 해결책

```bash
# 1. Producer 재시작
docker restart producer-stock

# 2. 수동 테스트 메시지 발행
docker exec kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic stock-ticks

# 3. 테스트 메시지 (JSON 형식)
{"code": "005930", "price": 75000, "rate": 1.5, "timestamp": "2025-12-24T14:30:00+09:00"}

# 4. 테스트 메시지 수신 확인
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --from-beginning \
  --max-messages 1
```

---

## 🚨 증상 5: "WebSocket 메시지는 오는데 차트가 안 움직여요"

### 원인: 프론트엔드 콜백 로직 실패

**확인 방법**:
```javascript
// StockDetailCard.vue에서 subscribeToStock 콜백 확인

const subscribeToStock = async (stockCode) => {
  try {
    const unsubscribe = await websocketService.subscribeStock(
      stockCode, 
      (message) => {
        console.log("🎯 WebSocket 메시지 수신:", message);  // ← 로깅 추가
        
        if (message.type === 'chart_update') {
          const { price, rate, timestamp } = message.data;
          console.log("📊 차트 업데이트:", { price, rate, timestamp });
          
          // 실시간 가격 업데이트
          currentPrice.value = price;
          currentChangeRate.value = rate;
          
          // 부모 컴포넌트에 알림
          emit('updatePrice', { price, rate, timestamp });
        } else {
          console.warn("⚠️  예상치 못한 메시지 타입:", message.type);
        }
      }
    );
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) {
    console.error('❌ WebSocket 구독 실패:', err);
  }
};
```

**해결책**:
```javascript
// 메시지 형식 확인
// 백엔드에서 보내는 메시지:
// {
//   "type": "chart_update",
//   "data": {
//     "code": "005930",
//     "price": 76000,
//     "rate": 2.5,
//     "timestamp": "2025-12-24T14:30:00+09:00"
//   }
// }

// message.data에서 필요한 필드 추출 확인
if (message.type === 'chart_update') {
  const data = message.data;
  console.log("Code:", data.code);      // 종목 코드
  console.log("Price:", data.price);    // 현재가
  console.log("Rate:", data.rate);      // 변화율
  console.log("Timestamp:", data.timestamp); // 시간
}
```

---

## 📊 정상 작동 확인 체크리스트

### ✅ 모든 단계 확인

```bash
# 단계 1: 컨테이너 모두 실행 중?
docker ps | grep -E "backend|kafka|elasticsearch|producer-stock"

# 단계 2: Kafka 토픽이 있는가?
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 | grep stock-ticks

# 단계 3: Producer가 데이터를 발행하는가?
docker logs producer-stock | grep -E "publish|발행" | tail -5

# 단계 4: Django가 Kafka Bridge를 시작했는가?
docker logs backend | grep "Stock Ticks Consumer"

# 단계 5: WebSocket 연결이 되는가?
# → 브라우저에서 주식 종목 선택 후 DevTools Console에서 로그 확인
```

### ✅ 브라우저 DevTools 확인

```javascript
// Console 탭에서 실행
// 1. WebSocket 연결 확인
console.log(document.querySelectorAll('[class*="websocket"]'));

// 2. 최근 메시지 추적
// Console에서 다음 로그를 찾으세요:
// "[WebSocket 005930] 메시지 수신: {type: 'chart_update', ...}"

// 3. Network 탭 > WS 필터 > Messages 탭
// → 3초마다 또는 정기적으로 메시지가 오는지 확인
```

---

## 🎯 빠른 진단 명령어

```bash
#!/bin/bash
# 복사해서 터미널에 실행

echo "=== 1. 컨테이너 상태 ==="
docker ps --format "table {{.Names}}\t{{.Status}}"

echo -e "\n=== 2. Kafka 토픽 ==="
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep stock

echo -e "\n=== 3. Django 로그 (마지막 20줄) ==="
docker logs backend 2>/dev/null | tail -20

echo -e "\n=== 4. Producer 로그 (마지막 10줄) ==="
docker logs producer-stock 2>/dev/null | tail -10

echo -e "\n=== 5. Elasticsearch 상태 ==="
curl -s http://localhost:9200/ | grep -o '"version".*' || echo "ES 미연결"

echo -e "\n=== 진단 완료 ==="
```

---

## 💡 추가 팁

### 실시간 모니터링

```bash
# 터미널 1: Kafka 메시지 모니터링
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --from-beginning

# 터미널 2: Django 로그 모니터링 (실시간)
docker logs -f backend

# 터미널 3: 브라우저에서 주식 종목 선택 후 데이터 흐름 추적
```

### 테스트 메시지 발행

```bash
# Kafka에 직접 메시지 발행 (원본 데이터 없을 때)
docker exec kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic stock-ticks << EOF
{"code": "005930", "price": 75000, "rate": 1.5, "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S%z)"}
EOF
```

### 메모리/로그 정리

```bash
# Docker 불필요한 로그 정리
docker system prune -a --volumes

# 또는 특정 컨테이너 로그만 정리
docker logs --tail 0 -f backend  # 새 로그만 표시
```

---

## 📞 문제 해결 우선순위

| 우선순위 | 확인 항목 | 명령어 |
|---------|---------|--------|
| 🔴 1순위 | 컨테이너 실행 | `docker ps` |
| 🔴 1순위 | Kafka 토픽 | `docker exec kafka kafka-topics --list` |
| 🟠 2순위 | Django 로그 | `docker logs backend` |
| 🟠 2순위 | Producer 데이터 | `docker logs producer-stock` |
| 🟡 3순위 | WebSocket 연결 | 브라우저 DevTools Console |
| 🟡 3순위 | Kafka 메시지 | `kafka-console-consumer` |
| 🟢 4순위 | 성능 최적화 | 메모리/CPU 사용률 확인 |

---

## 📚 참고 자료

- [Django Channels](https://channels.readthedocs.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [WebSocket MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Vue.js Reactivity](https://vuejs.org/guide/extras/reactivity-in-depth.html)
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

---

**마지막 팁**: 문제가 해결되지 않으면 위의 진단 명령어들을 모두 실행한 결과를 수집한 후, 팀에 공유하세요! 📋
