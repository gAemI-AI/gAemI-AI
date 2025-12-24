# 📊 대시보드 실시간 데이터 - 완벽 가이드

> **질문**: "대시보드 페이지에서 차트 부분이 실시간 데이터가 반영되고 있는건지 모르겠어"

---

## ✅ 짧은 답변

**네, 실시간 데이터가 반영될 수 있도록 설계되었습니다.**

대시보드의 차트는 다음과 같이 작동합니다:

1. **초기 로드 (REST API)**
   - 종목 선택 시 과거 차트 데이터 로드
   - 예: 1주일, 1개월 등의 캔들 차트

2. **실시간 업데이트 (WebSocket)**
   - Kafka → Django Channel → WebSocket
   - 가격과 변화율이 실시간으로 갱신됨
   - 부모 컴포넌트에 이벤트 발생

---

## 🔍 확인 방법 (5가지)

### 방법 1️⃣: 브라우저 DevTools

```
F12 → Console 탭
다음 메시지를 찾으세요:

✅ 성공:
"[005930] WebSocket 연결 성공"
"[WebSocket 005930] 메시지 수신: {type: 'chart_update', ...}"

❌ 실패:
아무 메시지도 없거나 에러 메시지
```

### 방법 2️⃣: 디버그 패널 (권장) 🆕

```
오른쪽 아래 "🔍 실시간 데이터 모니터" 버튼 클릭
→ WebSocket 탭에서 연결 상태 및 메시지 확인
→ Performance 탭에서 수신율 및 응답시간 확인
```

### 방법 3️⃣: Docker 로그

```bash
# Kafka 메시지 확인
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --from-beginning \
  --max-messages 5

# Django 로그 확인
docker logs backend | grep "Chart WS"
```

### 방법 4️⃣: Network 탭

```
F12 → Network 탭 → WS 필터
→ ws://localhost:8000/ws/stocks/... 클릭
→ Messages 탭에서 메시지 흐름 확인
```

### 방법 5️⃣: 수동 테스트

```bash
# Kafka에 직접 메시지 발행
docker exec kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic stock-ticks

# 아래를 입력:
{"code": "005930", "price": 76000, "rate": 2.5, "timestamp": "2025-12-24T14:30:00+09:00"}
```

---

## 📚 상세 가이드

### 📖 아키텍처 이해하기
→ [REALTIME_DATA_FLOW.md](REALTIME_DATA_FLOW.md)

**포함 내용**:
- 전체 데이터 흐름도
- 각 컴포넌트 상세 설명
- REST API vs WebSocket 비교
- 정상 작동 신호

### 🔧 문제 해결하기
→ [TROUBLESHOOTING_REALTIME.md](TROUBLESHOOTING_REALTIME.md)

**포함 내용**:
- 증상별 진단 (5가지)
- 원인과 해결책
- 단계별 디버깅 플로우
- Docker 명령어 모음

### 🔍 디버그 패널 사용
→ [DEBUG_PANEL_GUIDE.md](DEBUG_PANEL_GUIDE.md)

**포함 내용**:
- 설치 및 활성화 방법
- 각 탭별 기능 설명
- 문제별 진단 방법
- 고급 활용법

### 🚀 자동 진단 스크립트
→ [diagnose_realtime.sh](diagnose_realtime.sh)

**실행 방법**:
```bash
bash diagnose_realtime.sh
```

---

## 🎯 빠른 체크리스트

실시간 데이터가 작동하는지 5초 안에 확인:

```
[ ] 1. 종목 선택 후 차트가 표시되는가? (초기 로드 확인)
      ↓
[ ] 2. DevTools에서 "[code] WebSocket 연결 성공" 메시지가 있는가?
      ↓
[ ] 3. 3초마다 "[WebSocket] 메시지 수신" 로그가 쌓이는가?
      ↓
[ ] 4. 차트의 가격이 자동으로 변하는가? (가격 필드 확인)
      ↓
[ ] 5. 모두 "체크"이면 → ✅ 정상 작동!
```

---

## 🐛 자주 나오는 문제 (FAQ)

### Q1: "차트는 보이는데 가격이 안 변해요"

**A1**: 
1. DevTools Console에서 WebSocket 연결 로그 확인
2. 메시지는 오는데 화면이 안 바뀌면 → 프론트엔드 콜백 에러
3. 메시지가 안 오면 → Kafka 브리지 미작동

```bash
# 진단 명령어
docker logs backend | grep "Stock Ticks Consumer"
```

---

### Q2: "Elasticsearch에는 데이터 있는데 API 응답이 없어요"

**A2**: 
1. StockChartView가 올바른 집계 쿼리를 하는지 확인
2. Elasticsearch 인덱스 매핑 확인

```bash
# 테스트 API 호출
curl "http://localhost:8000/api/v1/stocks/005930/chart/?range=1d&interval=1m"
```

---

### Q3: "로그에 아무것도 안 뜬다"

**A3**: Kafka Bridge가 시작되지 않음

```python
# backend-pjt/notifications/apps.py에 추가
def ready(self):
    from notifications.kafka_bridge import kafka_bridge
    kafka_bridge.start_all_consumers()
```

---

### Q4: "마켓 지수(KOSPI, KOSDAQ)는 실시간 업데이트가 안 되는데?"

**A4**: 정상입니다. 현재 마켓 지수는 초기 로드만 지원합니다.
(WebSocket 구독은 주식 종목만 구현됨)

---

## 🔄 데이터 흐름 한눈에 보기

```
┌─────────────────┐
│ 주식 시세 소스   │
└────────┬────────┘
         │
         ↓ Kafka
    ┌────────────┐
    │stock-ticks│
    └────┬───────┘
         │
    ┌────┴─────────────┐
    │                  │
    ↓ Consumer         ↓ Flink
┌────────────────┐  ┌──────────┐
│Kafka Bridge    │  │Processing│
│(Django Channel)│  │(Analytics│
└────┬───────────┘  └──────────┘
     │
     ↓ WebSocket Group Send
┌─────────────────────┐
│ ChartConsumer (모든 │
│ 연결된 클라이언트)   │
└────┬────────────────┘
     │
     ↓ WebSocket
┌──────────────────────────┐
│ 브라우저 클라이언트       │
│ StockDetailCard.vue      │
│ - currentPrice 갱신      │
│ - emit('updatePrice')    │
└──────────────────────────┘
```

---

## 💡 핵심 포인트

### ✨ 3개 구성 요소

1. **REST API** (초기 데이터)
   - 엔드포인트: `/api/v1/stocks/{code}/chart/`
   - 반환: 과거 캔들 데이터 배열

2. **Kafka** (실시간 메시지)
   - 토픽: `stock-ticks`
   - 메시지: `{"code": "005930", "price": 75000, "rate": 1.5}`

3. **WebSocket** (실시간 전송)
   - URL: `ws://localhost:8000/ws/stocks/{code}/`
   - 메시지: `{"type": "chart_update", "data": {...}}`

### 🎯 각 컴포넌트의 역할

| 컴포넌트 | 역할 |
|---------|------|
| StockDetailCard.vue | 차트 렌더링 + WebSocket 구독 |
| websocketService.js | WebSocket 연결/해제 관리 |
| ChartConsumer | Kafka 메시지를 WebSocket으로 중계 |
| KafkaBridge | Kafka Consumer 시작 및 관리 |
| StockChartView | 초기 차트 데이터 제공 (ES 쿼리) |

---

## 🚀 다음 단계

### 즉시 확인해야 할 것
1. 디버그 패널 설치 ([DEBUG_PANEL_GUIDE.md](DEBUG_PANEL_GUIDE.md) 참고)
2. 브라우저에서 WebSocket 연결 상태 확인
3. Kafka 메시지 실제로 도착하는지 확인

### 개선할 수 있는 것
1. 마켓 지수도 WebSocket 실시간 구독 추가
2. 차트 배열도 점진적으로 업데이트 (현재는 가격만)
3. WebSocket 재연결 로직 강화
4. 메시지 throttle/debounce 추가 (고빈도 데이터)

### 심화 학습
- [REALTIME_DATA_FLOW.md](REALTIME_DATA_FLOW.md) 정독
- [TROUBLESHOOTING_REALTIME.md](TROUBLESHOOTING_REALTIME.md)의 모든 진단 명령어 실행
- 각 컴포넌트 소스 코드 리뷰

---

## 🎓 학습 목표 체크

이 가이드를 읽은 후:

- [ ] WebSocket 기본 개념 이해
- [ ] Kafka와 Channel Layers의 역할 이해
- [ ] 전체 데이터 파이프라인 그릴 수 있음
- [ ] 문제 발생 시 자가 진단 가능
- [ ] 디버그 패널로 실시간 모니터링 가능

---

## 📞 추가 지원

### 문서
- `REALTIME_DATA_FLOW.md`: 상세 아키텍처
- `TROUBLESHOOTING_REALTIME.md`: 문제 해결
- `DEBUG_PANEL_GUIDE.md`: 디버그 도구
- `diagnose_realtime.sh`: 자동 진단

### 명령어
```bash
# 전체 시스템 진단
bash diagnose_realtime.sh

# Kafka 메시지 모니터링
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic stock-ticks --from-beginning

# Django 로그 실시간 모니터
docker logs -f backend
```

### 파일 위치
```
gaemi-project/
├── REALTIME_DATA_FLOW.md              ← 전체 아키텍처
├── TROUBLESHOOTING_REALTIME.md        ← 문제 해결
├── DEBUG_PANEL_GUIDE.md               ← 디버그 도구
├── diagnose_realtime.sh               ← 자동 진단
└── frontend-pjt/
    └── src/
        ├── components/
        │   ├── dashboard/
        │   │   └── StockDetailCard.vue ← 차트 컴포넌트
        │   └── debug/
        │       └── RealtimeDebugPanel.vue ← 디버그 패널 🆕
        └── services/
            └── websocketService.js    ← WS 서비스
```

---

**작성 일시**: 2025-12-24  
**버전**: 1.0  
**대상**: gAemI 팀 모든 개발자

Happy debugging! 🚀
