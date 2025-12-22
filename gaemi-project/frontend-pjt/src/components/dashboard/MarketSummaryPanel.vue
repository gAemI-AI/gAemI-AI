<template>
  <div class="market-panel">
    <h3 class="panel-title">시장 지수</h3>

    <!-- 로딩 -->
    <div v-if="market.isLoading" class="empty">
      시장 지수 불러오는 중...
    </div>

    <!-- 데이터 없음 -->
    <div v-else-if="!market.kospi && !market.kosdaq" class="empty">
      시장 지수 데이터가 없습니다.
    </div>

    <div v-else class="market-cards">
      <!-- 코스피 -->
      <div class="market-card" v-if="market.kospi">
        <div class="label">코스피</div>
        <div class="price">
          {{ market.kospi?.price.toLocaleString() }}
        </div>
        <div
          class="diff"
          :class="{ up: market.kospi.diff >= 0, down: market.kospi.diff < 0 }"
        >
          <span>
            {{ market.kospi.diff >= 0 ? "▲" : "▼" }}
            {{ market.kospi.diff }}
          </span>
          <span>({{ market.kospi.rate }}%)</span>
        </div>
      </div>


      <!-- 코스닥 -->
      <div class="market-card" v-if="market.kosdaq">
        <div class="label">코스닥</div>
        <div class="price">
          {{ market.kosdaq?.price.toLocaleString() }}
        </div>
        <div
          class="diff"
          :class="{ up: market.kosdaq.diff >= 0, down: market.kosdaq.diff < 0 }"
        >
          <span>
            {{ market.kosdaq.diff >= 0 ? "▲" : "▼" }}
            {{ market.kosdaq.diff }}
          </span>
          <span>({{ market.kosdaq.rate }}%)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useMarketStore } from "@/stores/marketStore";

console.log("🔥 MarketSummaryPanel script loaded");

const market = useMarketStore();

onMounted(() => {
  console.log("🔥 MarketSummaryPanel mounted");
  market.fetchMarketIndex(); // 🔹 지금은 더미
});
</script>

<style scoped>
.market-panel {
  background: #ffffff;
  border-radius: 14px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

/* 카드 2개 */
.market-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.market-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 12px;
}

.label {
  font-size: 12px;
  color: #6b7280;
}

.price {
  font-size: 20px;
  font-weight: 700;
  margin: 4px 0;
}

.diff {
  font-size: 13px;
  display: flex;
  gap: 6px;
}

.diff.up {
  color: #ef4444;
}

.diff.down {
  color: #2563eb;
}
</style>
