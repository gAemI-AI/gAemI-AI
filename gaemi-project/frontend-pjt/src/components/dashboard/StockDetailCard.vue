<template>
  <div class="detail-card">
    <header class="detail-header">
      <div>
        <div class="name">
          {{ stock.name }}
          <span class="code">{{ stock.code }}</span>
        </div>
        <div class="price-row">
          <span class="price">{{ stock.price.toLocaleString() }}원</span>
          <span
            class="change"
            :class="{ up: stock.change > 0, down: stock.change < 0 }"
          >
            {{ stock.change > 0 ? '+' : '' }}{{ stock.change.toLocaleString() }}원
            ({{ stock.changeRate.toFixed(2) }}%)
          </span>
        </div>
      </div>

      <div class="range-buttons">
        <button
          v-for="r in ranges"
          :key="r.value"
          class="range-btn"
          :class="{ active: r.value === selectedRange }"
          @click="selectedRange = r.value"
        >
          {{ r.label }}
        </button>
      </div>
    </header>

    <!-- 가격 추이 차트 (간단한 SVG 라인) -->
    <section class="chart-section">
      <div class="chart-title">가격 추이</div>
      <svg viewBox="0 0 100 40" class="line-chart">
        <polyline
          :points="linePoints"
          fill="none"
          stroke-width="2"
          stroke="#2563eb"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <div class="chart-x-axis">
        <span v-for="(label, idx) in xLabels" :key="idx">{{ label }}</span>
      </div>
    </section>

    <!-- 거래량 바 차트 흉내 -->
    <section class="chart-section">
      <div class="chart-title">거래량</div>
      <div class="bars">
        <div
          v-for="(v, idx) in volumes"
          :key="idx"
          class="bar-wrapper"
        >
          <div class="bar" :style="{ height: (v / maxVolume) * 60 + 'px' }" />
          <div class="bar-label">{{ xLabels[idx] }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue';
import websocketService from '@/services/websocketService';

const props = defineProps({
  stock: { type: Object, required: true },
});

const emit = defineEmits(['updatePrice']);

const ranges = [
  { label: '1D', value: '1D' },
  { label: '1W', value: '1W' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
];

const selectedRange = ref('1W');

// 차트 데이터 (실시간 업데이트)
const xLabels = ref(['11월 14일', '11월 15일', '11월 16일', '11월 17일', '11월 18일', '11월 19일']);
const prices = ref([72000, 71500, 70500, 69800, 71000, 70680]);
const volumes = ref([900000, 1200000, 800000, 1000000, 1100000, 950000]);

const unsubscribeFunctions = ref([]);

// WebSocket 구독
const subscribeToStock = async (stockCode) => {
  try {
    const unsubscribe = await websocketService.subscribeStock(stockCode, (message) => {
      if (message.type === 'chart_update') {
        const { price, rate, timestamp } = message.data;
        
        // 가격 업데이트
        updateChartData(price, rate);
        
        // 부모 컴포넌트에 알림
        emit('updatePrice', { price, rate, timestamp });
      }
    });
    
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) {
    console.error(`WebSocket 구독 실패:`, err);
  }
};

// 차트 데이터 업데이트
const updateChartData = (newPrice, newRate) => {
  // 마지막 가격 제거 후 새 가격 추가 (최대 6개 유지)
  if (prices.value.length >= 6) {
    prices.value.shift();
    xLabels.value.shift();
    volumes.value.shift();
  }
  
  prices.value.push(newPrice);
  
  // 현재 시간 추가 (HHMM 형식)
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  xLabels.value.push(timeStr);
  
  // 더미 거래량 추가 (실제로는 백엔드에서 받아야 함)
  const dummyVolume = Math.floor(Math.random() * 1500000 + 500000);
  volumes.value.push(dummyVolume);
};

const maxPrice = computed(() => Math.max(...prices.value));
const minPrice = computed(() => Math.min(...prices.value));
const maxVolume = computed(() => Math.max(...volumes.value));

const linePoints = computed(() => {
  const width = 100;
  const height = 40;
  const stepX = width / (prices.value.length - 1) || 1;
  const range = maxPrice.value - minPrice.value || 1;

  return prices.value
    .map((p, i) => {
      const x = i * stepX;
      const y = height - ((p - minPrice.value) / range) * (height - 4) - 2;
      return `${x},${y}`;
    })
    .join(' ');
});

onMounted(() => {
  // stock.code가 있으면 구독 시작
  if (props.stock?.code) {
    subscribeToStock(props.stock.code);
  }
});

// stock.code 변경 시 구독 업데이트
watch(() => props.stock?.code, (newCode, oldCode) => {
  if (newCode && newCode !== oldCode) {
    // 이전 구독 해제
    unsubscribeFunctions.value.forEach(unsub => unsub());
    unsubscribeFunctions.value = [];
    
    // 새 종목 구독
    subscribeToStock(newCode);
  }
});

onUnmounted(() => {
  // 컴포넌트 언마운트 시 모든 구독 해제
  unsubscribeFunctions.value.forEach(unsub => unsub());
  unsubscribeFunctions.value = [];
});
</script>

<style scoped>
/* ======================= */
/*      카드 컨테이너      */
/* ======================= */
.detail-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ======================= */
/*       헤더           */
/* ======================= */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.name {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.4px;
}

.code {
  margin-left: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-row {
  margin-top: 12px;
  display: flex;
  gap: 12px;
  align-items: baseline;
  flex-wrap: wrap;
}

.price {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.5px;
}

.change {
  font-size: 13px;
  font-weight: 600;
}

.change.up {
  color: #ef4444;
}

.change.down {
  color: #2563eb;
}

/* ======================= */
/*      범위 버튼       */
/* ======================= */
.range-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
}

.range-btn {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.range-btn:hover {
  border-color: #d1d5db;
  background: #f9fafb;
  color: #4b5563;
}

.range-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

/* ======================= */
/*      차트 섹션      */
/* ======================= */
.chart-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  letter-spacing: -0.2px;
}

.line-chart {
  width: 100%;
  height: 160px;
  background: #f9fafb;
  border-radius: 12px;
  padding: 12px;
  box-sizing: border-box;
}

.chart-x-axis {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
  padding: 0 4px;
}

.bars {
  display: flex;
  gap: 6px;
  align-items: flex-end;
  height: 100px;
  padding: 0 4px;
}

.bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.bar {
  width: 100%;
  border-radius: 4px;
  background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
  transition: opacity 0.2s ease;
  min-height: 2px;
}

.bar:hover {
  opacity: 0.8;
}

.bar-label {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
}

/* ======================= */
/*      반응형         */
/* ======================= */
@media (max-width: 768px) {
  .detail-card {
    padding: 20px;
    gap: 20px;
  }

  .detail-header {
    flex-direction: column;
    gap: 12px;
  }

  .range-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .name {
    font-size: 16px;
  }

  .price {
    font-size: 22px;
  }

  .line-chart {
    height: 140px;
  }

  .bars {
    height: 80px;
  }
}

@media (max-width: 640px) {
  .detail-card {
    padding: 16px;
    gap: 16px;
  }

  .name {
    font-size: 15px;
  }

  .price {
    font-size: 20px;
  }

  .change {
    font-size: 12px;
  }

  .chart-title {
    font-size: 13px;
  }

  .line-chart {
    height: 120px;
  }

  .bars {
    height: 70px;
    gap: 4px;
  }

  .range-btn {
    padding: 5px 10px;
    font-size: 11px;
  }
}
</style>
