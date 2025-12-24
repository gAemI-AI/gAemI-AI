# 대시보드 차트 실시간 데이터 흐름 분석 보고서

## 📊 개요
대시보드의 차트가 실시간 데이터를 반영하는 메커니즘을 추적합니다.

---

## 🔄 데이터 흐름도

```
┌─────────────────────┐
│  외부 데이터 소스    │ (주식 시세, 시장 지수 등)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│  Producer (data-pjt/producer-stock/)        │
│  - 실시간 주식 시세 수집                     │
│  - Kafka 토픽으로 발행                       │
│  - 토픽: stock-ticks (체결가)               │
└──────────┬──────────────────────────────────┘
           │
           ▼ Kafka Broker
┌─────────────────────────────────────────────┐
│  Kafka Topics:                              │
│  • stock-ticks → 실시간 체결가               │
│  • stock-orderbook → 실시간 호가             │
│  • index-ticks → 시장 지수                  │
└──────────┬──────────┬───────────────────┬───┘
           │          │                   │
      ┌────▼──┐   ┌───▼────┐         ┌───▼────┐
      │Consumer│   │ Flink  │         │Consumer│
      │ Index  │   │ Jobs   │         │ (나머지)│
      └────────┘   └────────┘         └────────┘
           │
           ▼ Elasticsearch
┌─────────────────────────────────────────────┐
│  데이터 저장:                               │
│  • raw-stocks 인덱스                        │
│  • market-indices 인덱스 (시장 지수)        │
└──────────┬──────────────────────────────────┘
           │
    ┌──────┴─────────────────────────┐
    │                                 │
    ▼ Kafka Bridge                   ▼ 초기 데이터
┌──────────────────────────┐   ┌──────────────────────────┐
│ Django App               │   │ REST API                 │
│ (notifications app)      │   │ - /api/v1/stocks        │
│ • Kafka 컨슈머 시작      │   │ - /api/v1/stocks/{code} │
│ • WebSocket으로 전송      │   │ - /api/v1/stocks/chart  │
└──────────────┬───────────┘   │ - /api/v1/market/index  │
               │                └──────────┬───────────────┘
               │                           │
               │                           ▼
               │                   ┌──────────────────────┐
               │                   │ StockDetailCard.vue  │
               │                   │ • onMounted 시 호출  │
               │                   │ • 차트 데이터 로드    │
               │                   │ • 일일 거래량 로드    │
               │                   └──────────────────────┘
               │
               ▼ WebSocket 그룹
         (stock_{code})
               │
               ▼ 실시간 업데이트
       ┌───────────────────────────┐
       │ StockDetailCard.vue       │
       │ • currentPrice 갱신        │
       │ • currentChangeRate 갱신   │
       │ • 차트 강조 표시 가능      │
       └───────────────────────────┘
               │
               ▼ 부모 컴포넌트
         DashboardPage.vue
         (updatePrice 이벤트)
```

---

## 🔍 상세 분석

### 1️⃣ **프론트엔드: 초기 데이터 로드**

**파일**: [frontend-pjt/src/components/dashboard/StockDetailCard.vue](StockDetailCard.vue#L300-L320)

```javascript
// onMounted 시 실행
onMounted(() => {
  if (props.stock?.code) {
    loadChartData(selectedRange.value);      // 가격 추이 (1D/1W/1M/3M)
    loadDailyVolumes();                      // 거래량 (항상 1W)
    subscribeToStock(props.stock.code);      // WebSocket 실시간 구독
  }
});
```

**작동**:
- `loadChartData()`: REST API 호출 → `/stocks/{code}/chart/` 엔드포인트
- `loadDailyVolumes()`: 별도 REST API → `/stocks/{code}/chart/?range=1w&interval=1d`
- `subscribeToStock()`: WebSocket 연결 → `ws://localhost:8000/ws/stocks/{code}/`

---

### 2️⃣ **프론트엔드: REST API → 초기 차트 렌더링**

**파일**: [backend-pjt/stocks/views.py](stocks/views.py#L37-L125) - `StockChartView`

**API 엔드포인트**: `GET /api/v1/stocks/{code}/chart/?range=1d&interval=1m`

**처리 과정**:
```python
1. Elasticsearch 쿼리 실행
   └─ raw-stocks 인덱스에서 해당 종목의 시세 데이터 검색
   └─ range: 1d, 1w, 1m, 3m (조회 기간)
   └─ interval: 1m, 1d (집계 단위)

2. OHLC 캔들 생성
   └─ open: 해당 봉의 첫 체결가
   └─ high: 해당 봉의 최고가
   └─ low: 해당 봉의 최저가
   └─ close: 해당 봉의 마지막 체결가
   └─ volume: 거래량 합계

3. 응답 형식:
   [
     { "x": "2025-12-24T10:30:00+09:00", "y": [O, H, L, C], "v": 1000000 },
     ...
   ]
```

**⚠️ 주요 특징**:
- Elasticsearch의 `date_histogram` 집계 사용
- 시간대별 최고가, 최저가 자동 계산
- **차트는 초기 로드 후 자동으로 새로고침되지 않음** ← Kafka 브리지 필요!

---

### 3️⃣ **백엔드: WebSocket 연결 준비**

**파일**: [backend-pjt/gaemi_backend/routing.py](gaemi_backend/routing.py)

```python
websocket_urlpatterns = [
    re_path(r'ws/stocks/(?P<stock_code>\w+)/$', ChartConsumer.as_asgi()),
]
```

**파일**: [backend-pjt/notifications/consumers.py](notifications/consumers.py#L42-L61)

```python
class ChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stock_code = self.scope['url_route']['kwargs']['stock_code']
        self.group_name = f"stock_{self.stock_code}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"📈 [Chart WS Connected] Stock: {self.stock_code}")

    async def send_chart_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'chart_update',
            'data': data
        }))
```

---

### 4️⃣ **데이터 파이프라인: Kafka → WebSocket**

#### 4-1. 데이터 소스 (Producer)

**파일**: `data-pjt/producer-stock/main.py`
- 실시간 주식 시세 데이터 수집
- Kafka 토픽 `stock-ticks`로 발행
- 메시지 형식:
  ```json
  {
    "code": "005930",
    "price": 76000,
    "rate": 2.5,
    "timestamp": 1703424600000
  }
  ```

#### 4-2. Kafka 토픽 저장소

**토픽**: `stock-ticks`
- 실시간 체결가 데이터
- 이 토픽을 여러 consumer가 구독

#### 4-3. 데이터 처리 (Kafka Bridge)

**파일**: [backend-pjt/notifications/kafka_bridge.py](notifications/kafka_bridge.py#L71-L110)

```python
def start_stock_tick_consumer(self):
    """
    Kafka 토픽 'stock-ticks' 구독
    → WebSocket 그룹으로 브로드캐스트
    """
    def consume_ticks():
        consumer = KafkaConsumer(
            'stock-ticks',
            bootstrap_servers=[self.kafka_broker],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='websocket-stock-group',
        )
        
        for message in consumer:
            tick_data = message.value
            stock_code = tick_data.get('code')
            
            if stock_code:
                # 해당 종목을 구독한 모든 클라이언트에 전송
                async_to_sync(self.channel_layer.group_send)(
                    f"stock_{stock_code}",  # 그룹 이름
                    {
                        'type': 'send_chart_data',  # 호출할 메서드
                        'data': tick_data
                    }
                )
```

**작동 원리**:
1. Kafka의 `stock-ticks` 토픽 구독 (무한 루프)
2. 새로운 메시지 수신
3. Django Channel Layers의 `group_send()` 호출
4. 해당 그룹 내 모든 WebSocket 연결에 메시지 전송

---

### 5️⃣ **프론트엔드: WebSocket 메시지 처리**

**파일**: [frontend-pjt/src/services/websocketService.js](websocketService.js#L18-L80)

```javascript
subscribeStock(stockCode, callback) {
    const url = `${WS_BASE_URL}/ws/stocks/${stockCode}/`;
    
    return new Promise((resolve, reject) => {
        const socket = new WebSocket(url);
        
        socket.onmessage = (event) => {
            const response = JSON.parse(event.data);
            console.log(`[WebSocket ${stockCode}] 메시지 수신:`, response);
            
            // 모든 리스너에 전달
            const cbs = this.listeners.get(stockCode) || [];
            cbs.forEach(cb => cb(response));
        };
        
        // 연결 성공 시 언서브스크라이브 함수 반환
        socket.onopen = () => {
            resolve(() => this.unsubscribeStock(stockCode, callback));
        };
    });
}
```

**파일**: [frontend-pjt/src/components/dashboard/StockDetailCard.vue](StockDetailCard.vue#L232-L250)

```javascript
const subscribeToStock = async (stockCode) => {
  try {
    const unsubscribe = await websocketService.subscribeStock(
      stockCode, 
      (message) => {
        if (message.type === 'chart_update') {
          const { price, rate, timestamp } = message.data;
          
          // 실시간 가격 업데이트
          currentPrice.value = price;
          currentChangeRate.value = rate;
          
          // 부모 컴포넌트에 알림
          emit('updatePrice', { price, rate, timestamp });
        }
      }
    );
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) {
    console.error('WebSocket 구독 실패:', err);
  }
};
```

---

### 6️⃣ **부모 컴포넌트: 데이터 업데이트**

**파일**: [frontend-pjt/src/pages/DashboardPage.vue](DashboardPage.vue#L151-L160)

```javascript
// StockDetailCard에서 updatePrice 이벤트 수신
@updatePrice="updateSearchStockPrice"  // 검색 결과
@updatePrice="updateFavoriteStockPrice" // 관심종목

// 이벤트 핸들러
const updateSearchStockPrice = (data) => {
  if (searchSelectedStock.value) {
    searchSelectedStock.value.price = data.price;
    searchSelectedStock.value.changeRate = data.rate;
  }
};

const updateFavoriteStockPrice = (data) => {
  if (favoriteSelectedStock.value) {
    favoriteSelectedStock.value.price = data.price;
    favoriteSelectedStock.value.changeRate = data.rate;
  }
};
```

---

## 🎯 실시간 데이터가 작동하는지 확인하는 방법

### ✅ 체크리스트

| 항목 | 확인 방법 | 상태 |
|------|---------|------|
| **Kafka 연결** | `docker logs kafka` - 브로커 정상 실행 확인 | ? |
| **Producer 실행** | `docker logs producer-stock` - 데이터 발행 확인 | ? |
| **Kafka 토픽 데이터** | `kafka-console-consumer --topic stock-ticks` | ? |
| **Django 시작** | `docker logs backend` - "WebSocket 연결" 로그 확인 | ? |
| **Kafka Bridge 시작** | `docker logs backend` - "Alert Consumer 시작", "Stock Ticks Consumer 시작" 로그 | ? |
| **클라이언트 연결** | 브라우저 DevTools > Network > WS | ? |
| **메시지 수신** | 브라우저 DevTools Console - `[WebSocket ...] 메시지 수신:` | ? |
| **가격 업데이트** | 대시보드 차트의 가격이 자동 갱신됨 | ? |

---

## 🐛 자주 발생하는 문제와 해결책

### 문제 1: "WebSocket 연결은 되지만 메시지가 안 옴"
**원인**: Kafka 브리지가 시작되지 않음
**해결책**:
```bash
# Django 앱에서 Kafka Bridge 시작 확인
docker logs backend | grep "Stock Ticks Consumer"
```

### 문제 2: "Kafka 메시지가 발행되지 않음"
**원인**: Producer가 실행 중이지 않음
**해결책**:
```bash
docker logs producer-stock
```

### 문제 3: "메시지는 오지만 차트가 안 업데이트됨"
**원인**: 
- WebSocket 메시지 형식이 잘못됨
- 컴포넌트 콜백이 `chart_update` 메시지만 처리함
**해결책**:
```javascript
// 브라우저 DevTools에서 메시지 형식 확인
// { type: 'chart_update', data: { price, rate, timestamp } }
```

---

## 📋 데이터 업데이트 흐름 요약

```
현재 상황 (정상 작동):
1. 초기 로드 (REST API)
   └─ StockDetailCard.onMounted → loadChartData() → 차트 렌더링 ✅

2. 실시간 업데이트 (WebSocket)
   └─ Producer → Kafka (stock-ticks) 
   └─ Kafka Bridge (Consumer)
   └─ Django Channel Layer (group_send)
   └─ ChartConsumer (send_chart_data)
   └─ WebSocket 클라이언트
   └─ 콜백: currentPrice, currentChangeRate 업데이트 ✅
   └─ 부모 컴포넌트에 이벤트 전달 ✅
```

---

## 🚀 개선 제안

### 1. 차트 데이터 추가 업데이트
현재: 가격 정보만 실시간 업데이트
권장: 차트 배열 자체도 실시간으로 추가/갱신

```javascript
// 현재 (정보성만 업데이트)
currentPrice.value = price;
currentChangeRate.value = rate;

// 개선 (차트 배열도 추가)
prices.value.push(price);  // 또는 이동 평균선 계산
// 스크롤 자동 조정
if (chartContainer.value) {
  chartContainer.value.scrollLeft = chartContainer.value.scrollWidth;
}
```

### 2. 에러 처리 강화
```javascript
// WebSocket 재연결 로직 추가
// 일시적 끊김 시 자동으로 재구독
```

### 3. 성능 최적화
- 높은 빈도의 메시지는 throttle/debounce 적용
- 화면에 표시되지 않은 종목은 구독 해제

---

## 📊 마켓 인덱스 (KOSPI, KOSDAQ) 실시간 업데이트

**파일**: [frontend-pjt/src/components/dashboard/MarketSummaryPanel.vue](MarketSummaryPanel.vue#L56-L61)

```javascript
onMounted(() => {
  market.fetchMarketIndex();  // REST API 호출
  // ⚠️ WebSocket 구독은 없음 → 일회성 로드만
});
```

**문제점**:
- 마켓 지수는 초기 로드 후 실시간 업데이트 없음
- Kafka `index-ticks` 토픽이 있지만 프론트에서 구독하지 않음

**개선 방안**:
- WebSocket으로 시장 지수도 실시간 구독

---

## ✨ 결론

✅ **실시간 차트 업데이트 흐름은 제대로 구현되어 있습니다:**
1. REST API로 초기 차트 데이터 로드
2. WebSocket으로 실시간 체결가 수신
3. Vue 반응형 상태 업데이트
4. UI 자동 렌더링

⚠️ **확인 필요한 사항:**
- Kafka Producer가 `stock-ticks` 토픽에 데이터 발행 중인지
- Django 서버에서 Kafka Bridge가 정상 시작되었는지
- 브라우저 DevTools에서 WebSocket 메시지가 수신되는지

💡 **개선 권장사항:**
- 마켓 지수도 WebSocket 실시간 구독
- 차트 배열도 점진적으로 업데이트
- WebSocket 재연결 로직 추가
