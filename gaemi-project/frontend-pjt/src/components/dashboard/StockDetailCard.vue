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
import { computed, ref } from 'vue';

const props = defineProps({
  stock: { type: Object, required: true },
});

const ranges = [
  { label: '1D', value: '1D' },
  { label: '1W', value: '1W' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
];

const selectedRange = ref('1W');

// 더미 데이터 (나중에 API 응답으로 교체)
const xLabels = ['11월 14일', '11월 15일', '11월 16일', '11월 17일', '11월 18일', '11월 19일'];
const prices = [72000, 71500, 70500, 69800, 71000, 70680];
const volumes = [900000, 1200000, 800000, 1000000, 1100000, 950000];

const maxPrice = Math.max(...prices);
const minPrice = Math.min(...prices);
const maxVolume = Math.max(...volumes);

const linePoints = computed(() => {
  const width = 100;
  const height = 40;
  const stepX = width / (prices.length - 1);
  const range = maxPrice - minPrice || 1;

  return prices
    .map((p, i) => {
      const x = i * stepX;
      const y = height - ((p - minPrice) / range) * (height - 4) - 2;
      return `${x},${y}`;
    })
    .join(' ');
});
</script>

<style scoped>
.detail-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.name {
  font-size: 18px;
  font-weight: 700;
}
.code {
  margin-left: 4px;
  font-size: 12px;
  color: #9ca3af;
}
.price-row {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  align-items: baseline;
}
.price {
  font-size: 22px;
  font-weight: 700;
}
.change {
  font-size: 14px;
}
.change.up {
  color: #ef4444;
}
.change.down {
  color: #2563eb;
}

.range-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}
.range-btn {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
}
.range-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.chart-section {
  margin-top: 8px;
}
.chart-title {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}
.line-chart {
  width: 100%;
  height: 160px;
  background: #f9fafb;
  border-radius: 10px;
  padding: 8px;
}
.chart-x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}
.bars {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  height: 90px;
}
.bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bar {
  width: 80%;
  border-radius: 4px;
  background: #e5e7eb;
}
.bar-label {
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}
</style>
