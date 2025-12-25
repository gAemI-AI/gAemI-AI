<template>
  <div class="detail-card">
    <header class="detail-header">
      <div>
        <div class="name">
          {{ stock.name }}
          <span class="code">{{ stock.code }}</span>
        </div>
        <div class="price-row">
          <span class="price">{{ currentPrice.toLocaleString() }}원</span>
          <span 
            class="change" 
            :class="{ 'txt-red': currentChangeRate > 0, 'txt-blue': currentChangeRate < 0 }"
          >
            {{ currentChangeRate > 0 ? '+' : '' }}{{ currentChangeRate.toFixed(2) }}%
          </span>
        </div>
      </div>
      
      <div class="range-buttons">
        <button v-for="r in ranges" :key="r.value" class="range-btn" 
          :class="{ active: r.value === selectedRange }"
          @click="changeRange(r.value)">
          {{ r.label }}
        </button>
      </div>
    </header>

    <section class="chart-section">
      <div class="chart-title">가격 추이 (Candle)</div>
      
      <div class="chart-scroll-container" ref="scrollContainer">
        <div class="chart-content" :style="{ width: svgWidth + 'px' }">
          <svg class="chart" :viewBox="`0 0 ${svgWidth} 200`" preserveAspectRatio="none" 
            @mousemove="handleChartHover" @mouseleave="hoveredIdx = null">
            
            <line x1="0" :y1="scaleY(maxPrice)" :x2="svgWidth" :y2="scaleY(maxPrice)" stroke="#e5e7eb" stroke-dasharray="2,2" />
            <line x1="0" :y1="scaleY(minPrice)" :x2="svgWidth" :y2="scaleY(minPrice)" stroke="#e5e7eb" stroke-dasharray="2,2" />
            
            <g v-for="(c, i) in candleData" :key="i">
              <line :x1="c.x" :y1="c.yHigh" :x2="c.x" :y2="c.yLow" :stroke="c.color" stroke-width="1" />
              <rect :x="c.x - c.width / 2" :y="c.yBodyTop" :width="c.width" :height="Math.max(1, c.bodyHeight)" :fill="c.color" />
            </g>

            <g v-if="hoveredIdx !== null">
              <line :x1="hoveredX" y1="0" :x2="hoveredX" y2="200" stroke="#6b7280" stroke-width="1" stroke-dasharray="3,3" />
              <line x1="0" :y1="hoveredY" :x2="svgWidth" :y2="hoveredY" stroke="#6b7280" stroke-width="1" stroke-dasharray="3,3" />
              <circle :cx="hoveredX" :cy="hoveredY" r="3" fill="white" stroke="#6b7280" stroke-width="2" />
            </g>
          </svg>

          <div v-if="hoveredIdx !== null" class="candle-tooltip" :style="{ left: tooltipLeft + 'px', top: '10px' }">
            <div class="tt-time">{{ hoveredInfo.time }}</div>
            <div class="tt-row"><span>시가</span> <span>{{ hoveredInfo.open }}</span></div>
            <div class="tt-row"><span>고가</span> <span class="txt-red">{{ hoveredInfo.high }}</span></div>
            <div class="tt-row"><span>저가</span> <span class="txt-blue">{{ hoveredInfo.low }}</span></div>
            <div class="tt-row"><span>종가</span> <span>{{ hoveredInfo.close }}</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="chart-section" style="margin-top: 24px;">
      <div class="chart-title">거래량 (최근 7일)</div>
      
      <div class="volume-chart" @mousemove="handleVolHover" @mouseleave="hoveredVolIdx = null">
        <svg class="volume-svg" viewBox="0 0 400 80" preserveAspectRatio="none">
          <rect 
            v-for="(item, idx) in volumeChartData" 
            :key="idx"
            :x="(idx / Math.max(1, volumeChartData.length)) * 400 + 6"
            :y="80 - (item.volume / maxVolumeDaily) * 70"
            :width="(400 / Math.max(1, volumeChartData.length)) - 12"
            :height="(item.volume / maxVolumeDaily) * 70"
            :fill="item.color"
            rx="2"
            :opacity="hoveredVolIdx === idx ? 1 : 0.7" 
          />
        </svg>

        <div v-if="hoveredVolIdx !== null" class="vol-tooltip" :style="{ left: volTooltipLeft + 'px' }">
          <div class="vt-date">{{ volumeChartData[hoveredVolIdx].label }}</div>
          <div class="vt-val">{{ volumeChartData[hoveredVolIdx].volume.toLocaleString() }}주</div>
        </div>
      </div>

      <div class="chart-x-axis">
        <span 
          v-for="(item, idx) in volumeChartData" 
          :key="idx"
          class="vol-label"
          :style="{ width: (100 / Math.max(1, volumeChartData.length)) + '%' }"
        >
          {{ item.shortLabel }}
        </span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import websocketService from '@/services/websocketService';
import api from '@/api/axios';

const props = defineProps({ stock: { type: Object, required: true }, });
const emit = defineEmits(['updatePrice']);

const ranges = [
  { label: '10초', value: '10S' },
  { label: '1분', value: '1D' }, 
];
const selectedRange = ref('10S');

const rawChartData = ref([]); 
const volumeChartData = ref([]); 

const isLoading = ref(false);
const scrollContainer = ref(null);

const hoveredIdx = ref(null);
const hoveredX = ref(0);
const hoveredY = ref(0);
const tooltipLeft = ref(0);

const hoveredVolIdx = ref(null);
const volTooltipLeft = ref(0);

const currentPrice = ref(props.stock?.price || 0);
const currentChange = ref(props.stock?.change || 0);
const currentChangeRate = ref(props.stock?.changeRate || 0);
const unsubscribeFunctions = ref([]);

const KST_OFFSET = 9 * 60 * 60 * 1000; 
const getCorrectTime = (timestamp) => new Date(timestamp - KST_OFFSET);

const CANDLE_WIDTH = 12; 
const CANDLE_GAP = 4;

const svgWidth = computed(() => {
  const contentWidth = rawChartData.value.length * (CANDLE_WIDTH + CANDLE_GAP) + 20; 
  return Math.max(600, contentWidth);
});

const scrollToRight = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollLeft = scrollContainer.value.scrollWidth;
    }
  });
};

const validData = computed(() => {
  if (!rawChartData.value.length) return [];
  return rawChartData.value.filter(d => d.y[3] > 0);
});

const visibleDataForScaling = computed(() => {
  if (!validData.value.length) return [];
  return validData.value.slice(-50); 
});

const minPrice = computed(() => {
  if (!visibleDataForScaling.value.length) return 0;
  const lows = visibleDataForScaling.value.map(d => d.y[2]);
  const min = Math.min(...lows);
  return min - (min * 0.001); 
});

const maxPrice = computed(() => {
  if (!visibleDataForScaling.value.length) return 100;
  const highs = visibleDataForScaling.value.map(d => d.y[1]);
  const max = Math.max(...highs);
  return max + (max * 0.001); 
});

const scaleY = (val) => {
  const h = 200;
  const padding = 10;
  let min = minPrice.value;
  let max = maxPrice.value;
  let range = max - min;
  
  if (range < 50) { 
    const mid = (min + max) / 2;
    min = mid - 25;
    max = mid + 25;
    range = 50;
  }
  return h - padding - ((val - min) / range) * (h - padding * 2);
};

const candleData = computed(() => {
  return rawChartData.value.map((d, i) => {
    if (!d.y || d.y.length < 4 || d.y[3] === 0) return null;
    const open = d.y[0];
    const high = d.y[1];
    const low = d.y[2];
    const close = d.y[3];
    const x = 10 + i * (CANDLE_WIDTH + CANDLE_GAP) + (CANDLE_WIDTH / 2);
    const isUp = close > open;
    const isDown = close < open;
    let color = '#374151';
    if (isUp) color = '#ef4444';
    if (isDown) color = '#2563eb';

    return {
      index: i,
      x: x,
      width: CANDLE_WIDTH,
      color: color,
      yHigh: scaleY(high),
      yLow: scaleY(low),
      yBodyTop: scaleY(Math.max(open, close)), 
      bodyHeight: Math.abs(scaleY(open) - scaleY(close)),
      info: {
        time: formatTime(d.x, selectedRange.value),
        open: open.toLocaleString(),
        high: high.toLocaleString(),
        low: low.toLocaleString(),
        close: close.toLocaleString()
      }
    };
  }).filter(c => c !== null);
});

const hoveredInfo = computed(() => {
  if (hoveredIdx.value === null) return {};
  return candleData.value[hoveredIdx.value]?.info || {};
});

const maxVolumeDaily = computed(() => {
  if (!volumeChartData.value.length) return 1;
  return Math.max(...volumeChartData.value.map(v => v.volume));
});

function handleChartHover(e) {
  if (!candleData.value.length) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const offsetX = e.clientX - rect.left; 
  const step = CANDLE_WIDTH + CANDLE_GAP;
  const foundCandle = candleData.value.find(c => Math.abs(c.x - offsetX) < step / 2);
  
  if(foundCandle) {
    hoveredIdx.value = candleData.value.indexOf(foundCandle);
    hoveredX.value = foundCandle.x;
    hoveredY.value = scaleY(rawChartData.value[foundCandle.index].y[3]); 
    tooltipLeft.value = foundCandle.x + 15;
    if (foundCandle.x > scrollContainer.value.scrollLeft + scrollContainer.value.clientWidth - 150) {
      tooltipLeft.value = foundCandle.x - 130;
    }
  }
}

function handleVolHover(e) {
  if (!volumeChartData.value.length) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const offsetX = e.clientX - rect.left;
  const width = rect.width;
  
  const count = volumeChartData.value.length;
  const itemWidth = width / count;
  let idx = Math.floor(offsetX / itemWidth);
  idx = Math.max(0, Math.min(idx, count - 1));

  hoveredVolIdx.value = idx;
  
  let left = (idx * itemWidth) + (itemWidth / 2);
  if (left < 50) left = 50;
  if (left > width - 50) left = width - 50;
  volTooltipLeft.value = left;
}

function changeRange(val) {
  selectedRange.value = val;
  rawChartData.value = [];
  loadChartData(val);
}

const loadChartData = async (range) => {
  if (!props.stock?.code) return;
  isLoading.value = true;
  try {
    const backendRange = range.toLowerCase();
    let interval = '1m'; 
    const response = await api.get(`/stocks/${props.stock.code}/chart/`, { params: { range: backendRange, interval } });
    if (Array.isArray(response.data)) { 
      rawChartData.value = response.data;
      scrollToRight();
    }
  } catch (err) { console.error(err); } finally { 
    isLoading.value = false;
  }
};

// ===============================================
// 📊 거래량 데이터 로드 + 네이버 증권 스타일 더미 데이터
// ===============================================
const loadDailyVolumes = async () => {
  try {
    const response = await api.get(`/stocks/${props.stock.code}/chart/`, { params: { range: '1w', interval: '1d' } });
    
    // 1. 실제 서버 데이터 매핑 (있다면 우선 사용)
    const realDataMap = {};
    if (Array.isArray(response.data)) {
      response.data.forEach(d => {
        let dateStr;
        if (typeof d.x === 'string') {
          dateStr = d.x.split('T')[0];
        } else {
          const dateObj = new Date(d.x);
          const year = dateObj.getFullYear();
          const month = String(dateObj.getMonth() + 1).padStart(2, '0');
          const day = String(dateObj.getDate()).padStart(2, '0');
          dateStr = `${year}-${month}-${day}`;
        }
        realDataMap[dateStr] = d;
      });
    }

    // 2. 요청하신 날짜 목록 (16, 17, 18, 19, 22, 23, 24)
    // 연도는 현재 시스템 설정에 맞춰 2025년으로 가정합니다.
    const targetDates = [
      '2025-12-16', '2025-12-17', '2025-12-18', '2025-12-19', 
      '2025-12-22', '2025-12-23', '2025-12-24'
    ];

    // 3. [하드코딩] 네이버 증권 스타일 "가상" 데이터 (실제 삼성전자 패턴 반영)
    // color: '#ef4444'(빨강/상승), '#2563eb'(파랑/하락)
    const mockDataMap = {
      '2025-12-16': { volume: 15420300, color: '#ef4444' }, // 상승
      '2025-12-17': { volume: 12150000, color: '#2563eb' }, // 하락
      '2025-12-18': { volume: 18700500, color: '#2563eb' }, // 하락 (거래량 터짐)
      '2025-12-19': { volume: 14200100, color: '#ef4444' }, // 반등
      '2025-12-22': { volume: 11500000, color: '#ef4444' }, // 상승
      '2025-12-23': { volume: 16800000, color: '#2563eb' }, // 하락
      '2025-12-24': { volume: 9800000,  color: '#ef4444' }, // 크리스마스 이브 (거래량 감소)
    };

    const filledData = targetDates.map(dateStr => {
      const dateObj = new Date(dateStr);
      const shortLabel = `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
      
      // A. 실제 데이터가 있으면 최우선 사용
      if (realDataMap[dateStr]) {
        const d = realDataMap[dateStr];
        const isUp = d.y[3] >= d.y[0];
        return {
          volume: d.v || 0,
          color: isUp ? '#ef4444' : '#2563eb',
          label: dateStr,
          shortLabel: shortLabel
        };
      } 
      
      // B. 실제 데이터 없으면 "그럴싸한 더미 데이터" 사용
      const mock = mockDataMap[dateStr];
      if (mock) {
        return {
          volume: mock.volume,
          color: mock.color,
          label: dateStr,
          shortLabel: shortLabel
        };
      }

      // C. 목록 외 날짜에 대한 예외 처리 (랜덤)
      return {
        volume: Math.floor(Math.random() * 5000000) + 5000000,
        color: '#374151',
        label: dateStr,
        shortLabel: shortLabel
      };
    });

    volumeChartData.value = filledData;

  } catch (err) { console.error('거래량 로드 에러:', err); }
};

const subscribeToStock = async (stockCode) => {
  try {
    const unsubscribe = await websocketService.subscribeStock(stockCode, (message) => {
      if (message.type === 'chart_update') {
        const { price, rate, timestamp } = message.data;
        currentPrice.value = price;
        currentChangeRate.value = rate;

        if (rawChartData.value.length > 0) {
          const lastData = rawChartData.value[rawChartData.value.length - 1];
          const currentT = getCorrectTime(timestamp);
          const lastT = getCorrectTime(lastData.x);

          let isSameCandle = false;
          if (selectedRange.value === '10S') {
             const currBucket = Math.floor(currentT.getTime() / 10000); 
             const lastBucket = Math.floor(lastT.getTime() / 10000);
             isSameCandle = currBucket === lastBucket;
          } else if (selectedRange.value === '1D') {
             isSameCandle = currentT.getMinutes() === lastT.getMinutes();
          }

          if (isSameCandle) {
            lastData.y[1] = Math.max(lastData.y[1], price);
            lastData.y[2] = Math.min(lastData.y[2], price);
            lastData.y[3] = price;
          } else {
            if (price > 0) {
              const newData = { x: timestamp, y: [price, price, price, price], v: 0 };
              rawChartData.value.push(newData);
              if(rawChartData.value.length > 2000) rawChartData.value.shift();
              scrollToRight(); 
            }
          }
        } else if (price > 0) {
            const newData = { x: timestamp, y: [price, price, price, price], v: 0 };
            rawChartData.value.push(newData);
            scrollToRight();
        }
        emit('updatePrice', { price, rate, timestamp });
      }
    });
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) { console.error(err); }
};

const formatTime = (ts, range) => {
  const date = getCorrectTime(ts);
  if (range === '10S') {
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
  } else if (range === '1D') {
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  } else {
    return `${date.getMonth()+1}/${date.getDate()}`;
  }
};

onMounted(() => { if (props.stock?.code) { loadChartData('10S'); loadDailyVolumes(); subscribeToStock(props.stock.code); } });
watch(() => props.stock?.code, (newCode) => { if (newCode) { unsubscribeFunctions.value.forEach(fn => fn()); unsubscribeFunctions.value = []; loadChartData('10S'); loadDailyVolumes(); subscribeToStock(newCode); } });
onUnmounted(() => { unsubscribeFunctions.value.forEach(fn => fn()); });
</script>

<style scoped>
.detail-card { background: white; border-radius: 16px; padding: 24px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; gap: 20px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #f3f4f6; padding-bottom: 16px; }
.name { font-size: 20px; font-weight: 700; color: #111827; }
.code { font-size: 13px; color: #9ca3af; margin-left: 6px; }
.price { font-size: 28px; font-weight: 800; color: #111827; margin-right: 8px; }

.change { font-size: 14px; font-weight: 600; padding: 4px 6px; border-radius: 6px; }
.change.txt-red { color: #ef4444; }
.change.txt-blue { color: #2563eb; }

.range-buttons { display: flex; gap: 4px; background: #f1f5f9; padding: 4px; border-radius: 8px; height: fit-content; }
.range-btn { padding: 4px 10px; font-size: 12px; font-weight: 600; border-radius: 6px; border: none; background: transparent; color: #64748b; cursor: pointer; }
.range-btn.active { background: white; color: #2563eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.chart-section { position: relative; width: 100%; }
.chart-title { font-size: 14px; font-weight: 700; color: #374151; margin-bottom: 8px; }

/* 캔들 차트 스크롤 */
.chart-scroll-container { width: 100%; height: 200px; overflow-x: auto; overflow-y: hidden; background: #fff; border-bottom: 1px solid #f3f4f6; position: relative; scrollbar-width: thin; }
.chart-scroll-container::-webkit-scrollbar { height: 6px; }
.chart-scroll-container::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
.chart-content { height: 100%; position: relative; }
.chart { width: 100%; height: 100%; cursor: crosshair; }

/* 캔들 툴팁 */
.candle-tooltip { position: absolute; background: rgba(30, 41, 59, 0.95); color: white; padding: 8px 12px; border-radius: 8px; font-size: 11px; z-index: 20; pointer-events: none; width: 110px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
.tt-time { font-size: 11px; color: #94a3b8; margin-bottom: 4px; border-bottom: 1px solid #475569; padding-bottom: 2px; }
.tt-row { display: flex; justify-content: space-between; margin-bottom: 2px; }
.txt-red { color: #f87171; }
.txt-blue { color: #60a5fa; }

/* 거래량 차트 */
.volume-chart { width: 100%; height: 80px; position: relative; cursor: pointer; }
.volume-svg { width: 100%; height: 100%; }

/* 거래량 툴팁 */
.vol-tooltip { 
  position: absolute; bottom: 85px; transform: translateX(-50%);
  background: rgba(30, 41, 59, 0.95); color: white; 
  padding: 6px 10px; border-radius: 6px; font-size: 11px; z-index: 20; pointer-events: none;
  white-space: nowrap; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.vol-tooltip::after {
  content: ''; position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%);
  border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid rgba(30, 41, 59, 0.95);
}
.vt-date { color: #94a3b8; font-size: 10px; margin-bottom: 2px; }
.vt-val { font-weight: 700; font-size: 12px; }

.chart-x-axis { display: flex; justify-content: space-between; margin-top: 4px; font-size: 11px; color: #9ca3af; text-align: center; }
.vol-label { display: block; text-align: center; }
</style>