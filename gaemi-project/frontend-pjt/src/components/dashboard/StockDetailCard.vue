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
          v-if="linePoints"
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
      <div class="chart-title">거래량 (최근 7일)</div>
      <div class="bars">
        <div
          v-for="(v, idx) in volumes"
          :key="idx"
          class="bar-wrapper"
        >
          <div class="bar" :style="{ height: (v / maxVolume) * 60 + 'px' }" />
          <div class="bar-label">{{ volumeLabels[idx] }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import api from "@/api/axios";
import { useChartSocketStore } from "@/stores/chartSocketStore";

const emit = defineEmits(["updatePrice"]);

const props = defineProps({
  stock: { type: Object, required: true },
});

const ranges = [
  { label: "1D", value: "1D" },
  { label: "1W", value: "1W" },
  { label: "1M", value: "1M" },
  { label: "3M", value: "3M" },
];

const selectedRange = ref("1D");

/* ===== 데이터 ===== */
const prices = ref([]);
const xLabels = ref([]);

const volumes = ref([]);
const volumeLabels = ref([]);

const chartSocketStore = useChartSocketStore();

const maxVolume = computed(() =>
  volumes.value.length ? Math.max(...volumes.value) : 1
);

/* ===== 과거 데이터 (거래량) ===== */
const fetchPriceChart = async () => {
  if (!props.stock?.code) return;

  prices.value = [];
  xLabels.value = [];

  try {
    const res = await api.get(`stocks/${props.stock.code}/chart/`, {
      params: {
        range: selectedRange.value.toLowerCase(),
        interval: "1d",
      },
    });

    const arr = Array.isArray(res.data) ? res.data : [];

    const parsed = arr
      .map((d) => {
        const price = Number(d.close ?? d.price ?? d.current_price);
        const rawLabel = d.x ?? d.timestamp ?? d.date ?? d.time;
        if (!Number.isFinite(price)) return null;
        return { price, label: rawLabel };
      })
      .filter(Boolean);

    prices.value = parsed.map((d) => d.price);
    xLabels.value = parsed.map((d) => {
      const dt = new Date(d.label);
      if (Number.isNaN(dt.getTime())) return String(d.label);
      return `${dt.getMonth() + 1}/${dt.getDate()}`;
    });
  } catch (e) {
    console.error("📉 chart fetch error", e);
  }
};

/* -----------------------------
  2) 거래량(API) - 최근 7일 고정 (range 무관)
  - 오늘 데이터가 생기면 다시 fetch해서 7개 유지
----------------------------- */
const fetchVolume7d = async () => {
  if (!props.stock?.code) return;

  try {
    const res = await api.get(`stocks/${props.stock.code}/chart/`, {
      params: {
        range: "1w",
        interval: "1d",
      },
    });

    const arr = Array.isArray(res.data) ? res.data: [];

    const parsed = arr
      .map((d) => {
        const volume = Number(d.volume ?? d.tick_volume ?? d.v ?? 0);
        const rawLabel = d.x ?? d.timestamp ?? d.date ?? d.time;
        const dt = new Date(rawLabel);
        const label = 
          Number.isNaN(dt.getTime())
          ? String(rawLabel)
          : `${dt.getMonth() + 1}/${dt.getDate()}`;
        return { volume: Number.isFinite(volume) ? volume : 0, label };
      })
      .filter(Boolean);
    
    // ✅ “최근 7개”만 유지 (왼쪽 오래된 것 제거, 오른쪽 최신 유지)
    const last7 = parsed.slice(-7);

    volumes.value = last7.map((d) => d.volume);
    volumeLabels.value = last7.map((d) => d.label);
  } catch (e) {
    console.error("📊 volume(7d) fetch error", e);
  }
};

/* -----------------------------
  3) WS 실시간: 가격 라인만 append
  - 거래량은 절대 만지지 않음
  - 날짜가 바뀌었으면(혹은 오늘 캔들이 생겼을 수 있으면) volume7d만 다시 fetch
----------------------------- */
const lastWsDayKey = ref(null);
const refetchVolumeLock = ref(false);

const dayKeyFromTs = (ts) => {
  const t = new Date(ts < 1e12 ? ts * 1000 : ts);
  return `${t.getFullYear()}-${t.getMonth() + 1}-${t.getDate()}`;
};

/* ===== 실시간 가격 ===== */
watch(
  () => chartSocketStore.ticks,
  async (ticks) => {
    if (!ticks?.length) return;

    const last = ticks[ticks.length - 1];
    const price = Number(last.price);
    const rate = Number(last.rate ?? 0);
    const ts = Number(last.timestamp);

    if (!Number.isFinite(price)) return;

    emit("updatePrice", {
      price,
      change: Math.round((price * rate) / 100),
      changeRate: rate,
    });

    // ✅ 가격 라인 append
    prices.value.push(price);

    const t = new Date(ts < 1e12 ? ts * 1000 : ts);
    const label = `${String(t.getHours()).padStart(2, "0")}:${String(t.getMinutes()).padStart(2, "0")}`;
    xLabels.value.push(label);

    if (prices.value.length > 80) {
      prices.value.shift();
      xLabels.value.shift();
    }

    // ✅ 날짜가 바뀌면 거래량 7일만 API로 다시 fetch (오늘 데이터 생겼을 수 있음)
    const dayKey = dayKeyFromTs(ts);

    if (lastWsDayKey.value == null) lastWsDayKey.value = dayKey;

    if (dayKey !== lastWsDayKey.value && !refetchVolumeLock.value) {
      lastWsDayKey.value = dayKey;

      // 연속 호출 방지(락)
      refetchVolumeLock.value = true;
      await fetchVolume7d();
      setTimeout(() => {
        refetchVolumeLock.value = false;
      }, 3000);
    }
  },
  { deep: true }
);

/* -----------------------------
  4) range 변경: 가격 차트만 다시 로딩
----------------------------- */
watch(selectedRange, async () => {
  await fetchPriceChart();
});

/* -----------------------------
  5) 종목 코드 바뀌면: 가격/거래량 둘 다 새로
----------------------------- */
watch(
  () => props.stock?.code,
  async (code, prev) => {
    if (!code || code === prev) return;

    lastWsDayKey.value = null;

    await fetchPriceChart();
    await fetchVolume7d();
  }
);
/* -----------------------------
  mounted
----------------------------- */
onMounted(async () => {
  chartSocketStore.connect(props.stock.code);
  await fetchPriceChart();
  await fetchVolume7d();
});

onUnmounted(() => {
});

/* -----------------------------
  SVG polyline
----------------------------- */
const linePoints = computed(() => {
  if (prices.value.length === 1) {
    prices.value.push(prices.value[0]);
    xLabels.value.push(xLabels.value[0]);
  }

  const max = Math.max(...prices.value);
  const min = Math.min(...prices.value);

  const safeMax = max === min ? max + 1 : max;
  const range = safeMax - min;

  const stepX = 100 / (prices.value.length - 1);

  return prices.value
    .map((p, i) => {
      if (!Number.isFinite(p)) return null;
      const x = i * stepX;
      const y = 40 - ((p - min) / range) * 36 - 2;
      return `${x},${y}`;
    })
    .filter(Boolean)
    .join(" ");
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
