# 🔍 실시간 데이터 디버그 패널 사용 가이드

## 📌 설치 및 활성화

### 1단계: 디버그 패널을 App.vue에 추가

파일: `frontend-pjt/src/App.vue`

```vue
<template>
  <RouterView />
  
  <!-- 🔍 실시간 데이터 디버그 패널 (개발 환경만) -->
  <RealtimeDebugPanel v-if="isDevelopment" />
</template>

<script setup>
import { RouterView } from 'vue-router';
import RealtimeDebugPanel from '@/components/debug/RealtimeDebugPanel.vue';

// 개발 환경 감지
const isDevelopment = import.meta.env.DEV || process.env.NODE_ENV === 'development';
</script>
```

### 2단계: StockDetailCard.vue 수정 (데이터 로깅 추가)

기존 코드에서 WebSocket 콜백 부분을 수정하세요:

```javascript
// backend-pjt/frontend-pjt/src/components/dashboard/StockDetailCard.vue

const subscribeToStock = async (stockCode) => {
  try {
    const unsubscribe = await websocketService.subscribeStock(stockCode, (message) => {
      if (message.type === 'chart_update') {
        const { price, rate, timestamp } = message.data;
        
        // 🔍 디버그 패널에 데이터 기록
        if (window.__realtimeDebug) {
          window.__realtimeDebug.recordMessage(stockCode, price, rate);
        }
        
        // 기존 로직
        currentPrice.value = price;
        currentChangeRate.value = rate;
        emit('updatePrice', { price, rate, timestamp });
      }
    });
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) {
    console.error('WebSocket 구독 실패:', err);
    
    // 🔍 에러 기록
    if (window.__realtimeDebug) {
      window.__realtimeDebug.recordError(
        'WebSocket 구독 실패',
        err.message
      );
    }
  }
};
```

---

## 🎯 사용 방법

### 1️⃣ 디버그 패널 열기
- 오른쪽 아래에 "🔍 실시간 데이터 모니터" 버튼 클릭
- 패널이 위로 열림

### 2️⃣ WebSocket 탭 (기본)
- **현재 연결된 종목들의 WebSocket 상태 표시**
- **최근 수신한 메시지 10개 확인**
- 종목 코드, 가격, 변화율, 수신 시간 표시
- 아래에 총 수신 메시지 개수 표시

### 3️⃣ Error Log 탭
- 발생한 모든 에러 메시지 확인
- 시간, 메시지, 상세 정보 표시
- 에러가 없으면 "✅ 에러 없음" 표시

### 4️⃣ Performance 탭
- **마지막 1분 수신율**: 지난 1분 동안 받은 메시지 수
- **평균 응답 시간**: 메시지 수신 시간 (ms)
- **최대 응답 시간**: 가장 오래 걸린 응답 시간
- **성능 성공율**: 에러 없이 성공한 메시지 비율

### 5️⃣ Settings 탭
- **기본 URL**: WebSocket 연결 주소 확인
- **자동 스크롤**: 새 메시지가 오면 자동으로 스크롤
- **알림음 활성화**: (향후 기능)
- **로그 초기화**: 모든 데이터 초기화
- **데이터 내보내기**: JSON 파일로 다운로드

---

## 🔧 기능별 해석 방법

### ✅ 정상 작동 신호

```
WebSocket 탭:
- 상태: 종목별로 "연결됨" 표시 (초록 점 🟢)
- 메시지 수신: 3초마다 또는 정기적으로 메시지 오는 중
- 마지막 1분 수신: 10개 이상
- 성공율: 95% 이상

Error Log 탭:
- "✅ 에러 없음" 표시
```

### ❌ 문제 신호

| 증상 | 원인 | 해결책 |
|------|------|--------|
| 연결됨이지만 메시지 안 옴 (🔴) | Kafka 브리지 미작동 | 백엔드 로그 확인 |
| "WebSocket 구독 실패" 에러 | 서버 주소 오류 | WebSocket URL 확인 |
| 메시지는 오지만 가격 안 바뀜 | 프론트 콜백 에러 | DevTools Console 확인 |
| 마지막 1분 수신: 0 | 데이터 발행 안 됨 | Producer 상태 확인 |

---

## 📊 실시간 데이터 흐름 추적 예시

### 시나리오: 삼성전자(005930) 선택 후 모니터링

```
1. 종목 선택 (클릭)
   ↓
2. WebSocket 탭에서:
   - 005930: 연결됨 (초록 점 🟢)
   
3. 몇 초 대기 후:
   - 메시지 로그에:
     14:32:15  005930  75,000원  +1.5%
     14:32:18  005930  75,050원  +1.6%
     14:32:21  005930  74,950원  +1.4%
   
4. Performance 탭:
   - 마지막 1분: 5개
   - 평균 응답시간: 45ms
   - 성공율: 100%
   
5. 모든 지표가 정상이면 ✅ 실시간 데이터가 제대로 작동 중
```

---

## 🐛 문제 해결 플로우

### 케이스 1: "메시지가 안 옴"

```javascript
// 브라우저 DevTools Console에서:
console.log(window.__realtimeDebug);

// 출력 결과 확인:
{
  recordMessage: ƒ,
  recordError: ƒ,
  recordResponseTime: ƒ,
  wsStatus: {},        // ← 빈 객체면 연결 안 됨
  recentMessages: [],  // ← 빈 배열이면 메시지 안 옴
  errorLog: []
}
```

**해결책**:
1. WebSocket 탭에서 상태 확인
2. 상태가 "미연결"이면 → 브라우저 콘솔에서 에러 메시지 확인
3. Error Log 탭에서 구체적인 에러 확인

---

### 케이스 2: "메시지는 오는데 차트가 안 움직여요"

```
Performance 탭에서:
- 마지막 1분 수신: 5개 ✅ (메시지 옴)
- 성공율: 100% ✅ (에러 없음)

그런데 차트가 안 움직임?
```

**진단**:
```javascript
// StockDetailCard.vue의 currentPrice 상태 확인
console.log('현재 가격:', currentPrice.value);
console.log('변화율:', currentChangeRate.value);

// Vue DevTools (확장 프로그램) 설치하여 상태 실시간 확인
```

**해결책**:
- StockDetailCard.vue의 콜백에서 `currentPrice.value = price;` 확인
- Vue 반응형 상태 업데이트 제대로 되는지 확인

---

## 🔍 고급 활용

### 데이터 내보내기 및 분석

```javascript
// Settings 탭에서 "데이터 내보내기" 클릭
// → realtime-data-{timestamp}.json 다운로드

// 파일 내용 예시:
{
  "messages": [
    {
      "code": "005930",
      "price": 75000,
      "rate": 1.5,
      "timestamp": 1703424735000
    },
    ...
  ],
  "errors": [],
  "responseTimes": [45, 38, 42, ...],
  "totalMessages": 125,
  "exportTime": "2025-12-24T14:32:15.000Z"
}
```

**분석 방법**:
```javascript
// 평균 가격 변화율 계산
const avgRate = messages.reduce((sum, m) => sum + m.rate, 0) / messages.length;

// 시간대별 메시지 수 그래프
const messagesByHour = messages.reduce((acc, m) => {
  const hour = new Date(m.timestamp).getHours();
  acc[hour] = (acc[hour] || 0) + 1;
  return acc;
}, {});
```

---

## 🚀 성능 최적화 활용

### 응답 시간 모니터링

디버그 패널의 **Performance 탭**에서:

```
평균 응답 시간: 45ms
  ↓
매우 좋음 (< 50ms): ✅
좋음 (50-100ms): ✅
보통 (100-200ms): ⚠️
나쁨 (> 200ms): ❌

만약 평균이 200ms 이상이면:
1. Kafka 브로커 성능 확인
2. WebSocket 메시지 빈도 조절
3. 메시지 크기 최소화
```

---

## 📱 모바일 환경에서 사용

패널이 자동으로 반응형으로 조정됩니다:

```
데스크톱:
┌─────────────────────────────┐
│  600px 너비 패널            │
└─────────────────────────────┘

모바일 (< 768px):
┌──────────────────────┐
│  화면 전체 너비      │  ← 하단 절반 높이
└──────────────────────┘
```

---

## 💡 팁 & 트릭

### 1. Console에서 직접 데이터 기록

```javascript
// 콘솔에서 수동으로 메시지 추가
window.__realtimeDebug.recordMessage('005930', 75100, 1.6);

// 에러 기록
window.__realtimeDebug.recordError('테스트 에러', '상세 내용');
```

### 2. 상태 모니터링

```javascript
// 실시간으로 최근 메시지 확인
window.__realtimeDebug.recentMessages
// → 배열 형태로 출력

// WebSocket 상태 확인
window.__realtimeDebug.wsStatus
// → { "005930": { state: "connected" }, ... }
```

### 3. 로그 자동 저장 (Python)

```python
# 서버에서 메트릭 수집하기
import json
from datetime import datetime

log_data = {
    "timestamp": datetime.now().isoformat(),
    "ws_connections": 5,
    "messages_per_minute": 125,
    "error_rate": 0.02
}

# 파일에 저장
with open("realtime-metrics.jsonl", "a") as f:
    f.write(json.dumps(log_data) + "\n")
```

---

## 🎓 학습 리소스

이 디버그 패널을 통해 다음을 배울 수 있습니다:

1. **WebSocket 동작 원리**
   - 연결 상태 추적
   - 메시지 송수신 과정

2. **실시간 데이터 파이프라인**
   - 지연 시간 측정
   - 데이터 손실률 확인

3. **성능 최적화**
   - 응답 시간 분석
   - 병목 지점 파악

4. **에러 처리**
   - 에러 발생 패턴 분석
   - 문제 근본 원인 파악

---

## 📞 지원

패널이 작동하지 않으면:

1. 브라우저 DevTools Console 확인
2. `window.__realtimeDebug` 객체 존재 확인
3. Vue DevTools에서 RealtimeDebugPanel 컴포넌트 확인
4. 개발 환경 설정 확인 (`isDevelopment` 값)

---

**Happy Debugging! 🚀**
