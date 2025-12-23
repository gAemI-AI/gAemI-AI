<template>
  <div class="market-panel">
    <h3 class="panel-title">시장 지수</h3>

    <div class="market-cards">
      <div class="market-card kospi-card">
        <div class="card-header">
          <span class="label">코스피</span>
          <span class="badge kospi-badge">인덱스</span>
        </div>
        
        <template v-if="market.kospi">
          <div class="price">{{ market.kospi.price.toLocaleString() }}</div>
          <div
            class="diff"
            :class="{ up: market.isKospiUp, down: !market.isKospiUp }"
          >
            <span class="diff-value">
              {{ market.isKospiUp ? "▲" : "▼" }}
              {{ Math.abs(market.kospi.diff) }}
            </span>
            <span class="diff-rate">({{ market.kospi.rate }}%)</span>
          </div>
        </template>
        
        <div v-else class="loading-text">
          {{ market.isLoading ? "로딩중..." : "데이터 없음" }}
        </div>
      </div>

      <div class="market-card kosdaq-card">
        <div class="card-header">
          <span class="label">코스닥</span>
          <span class="badge kosdaq-badge">인덱스</span>
        </div>

        <template v-if="market.kosdaq">
          <div class="price">{{ market.kosdaq.price.toLocaleString() }}</div>
          <div
            class="diff"
            :class="{ up: market.isKosdaqUp, down: !market.isKosdaqUp }"
          >
            <span class="diff-value">
              {{ market.isKosdaqUp ? "▲" : "▼" }}
              {{ Math.abs(market.kosdaq.diff) }}
            </span>
            <span class="diff-rate">({{ market.kosdaq.rate }}%)</span>
          </div>
        </template>

        <div v-else class="loading-text">
          {{ market.isLoading ? "로딩중..." : "데이터 없음" }}
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
  // ✅ loadMock() 대신 실제 API 호출로 변경
  market.fetchMarketIndex();
});
</script>

<style scoped>
.market-panel {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 16px;
  letter-spacing: -0.3px;
}

/* ======================= */
/* 카드 컨테이너     */
/* ======================= */
.market-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* ======================= */
/* 시장 카드         */
/* ======================= */
.market-card {
  border-radius: 12px;
  padding: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #f3f4f6;
  min-height: 100px; /* 로딩 중에도 최소 높이 유지 */
}

.kospi-card {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(244, 114, 114, 0.04) 100%);
  border-color: rgba(239, 68, 68, 0.2);
}

.kosdaq-card {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(59, 130, 246, 0.04) 100%);
  border-color: rgba(37, 99, 235, 0.2);
}

.market-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* ======================= */
/* 카드 헤더         */
/* ======================= */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.kospi-badge {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
}

.kosdaq-badge {
  background: rgba(37, 99, 235, 0.15);
  color: #1d4ed8;
}

/* ======================= */
/* 가격 정보         */
/* ======================= */
.price {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.diff {
  font-size: 13px;
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.diff-value {
  font-weight: 600;
}

.diff-rate {
  color: #9ca3af;
}

.diff.up {
  color: #ef4444;
}

.diff.down {
  color: #2563eb;
}

.loading-text {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 10px;
}

/* ======================= */
/* 반응형            */
/* ======================= */
@media (max-width: 640px) {
  .market-panel {
    padding: 16px;
  }

  .panel-title {
    font-size: 15px;
    margin-bottom: 12px;
  }

  .market-cards {
    gap: 10px;
  }

  .market-card {
    padding: 14px;
  }

  .price {
    font-size: 16px;
  }

  .label {
    font-size: 12px;
  }

  .badge {
    font-size: 10px;
    padding: 2px 6px;
  }
}
</style>