<!-- src/pages/DashboardPage.vue -->
<template>
  <div class="page-container">

    <!-- --------------------------------------- -->
    <!-- 🔍 검색창 -->
    <!-- --------------------------------------- -->
    <section class="left-column">
      <div class='search-bar-wrapper'>
        <StockSearchBar @search="onSearch" />
      </div>

      <!-- 🔎 검색 결과 -->
      <div v-if="searchKeyword" class="search-results">
        <StockTickerRow
          :stocks="filteredStocks"
          :selected-code="searchSelectedStock?.code"
          @select="onSelectFromSearch"
        />
      </div>

      <!-- 🔵 검색 결과 그래프 -->
      <div v-if="searchChartOpen && searchSelectedStock" class="chart-box">
        <div class="chart-header">
          <h3>{{ searchSelectedStock.name }} ({{ searchSelectedStock.code }})</h3>
          <FavoriteButton :stock="searchSelectedStock" />
        </div>
        <StockDetailCard
          :stock="searchSelectedStock"
          @updatePrice="updateSearchStockPrice"
        />
      </div>

      <!-- --------------------------------------- -->
      <!-- ⭐ 내 관심종목 -->
      <!-- --------------------------------------- -->
      <div class="favorite-section">
        <h3>내 관심종목</h3>

        <StockTickerRow
          :stocks="favoriteStocks"
          :selected-code="favoriteSelectedStock?.code"
          @select="onSelectFromFavorite"
        />
      </div>

      <!-- 🟣 관심종목 그래프 -->
      <div v-if="favoriteChartOpen && favoriteSelectedStock" class="chart-box">
        <div class="chart-header">
          <h3>{{ favoriteSelectedStock.name }} ({{ favoriteSelectedStock.code }})</h3>
          <FavoriteButton :stock="favoriteSelectedStock" />
        </div>
        <StockDetailCard
          :stock="favoriteSelectedStock"
          @updatePrice="updateFavoriteStockPrice"
        />
      </div>
    </section>

    <!-- --------------------------------------- -->
    <!-- 오른쪽 알림 패널 -->
    <!-- --------------------------------------- -->
    <aside class="right-column">
      <MarketSummaryPanel />
      <AlertHistoryList :alerts="alertsStore.alertEvents" />
    </aside>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import api from "@/api/axios";

/* components */
import StockSearchBar from "@/components/dashboard/StockSearchBar.vue";
import StockTickerRow from "@/components/dashboard/StockTickerRow.vue";
import StockDetailCard from "@/components/dashboard/StockDetailCard.vue";
import AlertHistoryList from "@/components/dashboard/AlertHistoryList.vue";
import FavoriteButton from "@/components/common/FavoriteButton.vue";
import MarketSummaryPanel from "@/components/dashboard/MarketSummaryPanel.vue";

/* stores */
import { useFavoritesStore } from "@/stores/favoritesStore";
import { useAlertsStore } from "@/stores/alertsStore";
import { useChartSocketStore } from "@/stores/chartSocketStore";

/* ----------------------------- */
/* Pinia Store (⚠️ 최상단) */
/* ----------------------------- */
const store = useFavoritesStore();
const alertsStore = useAlertsStore();
const chartSocketStore = useChartSocketStore();

/* ----------------------------- */
/* 상태 정의 */
/* ----------------------------- */
const stocks = ref([]);

/* 검색 */
const searchKeyword = ref("");
const searchSelectedStock = ref(null);
const searchChartOpen = ref(false);

/* 관심종목 */
const favoriteSelectedStock = ref(null);
const favoriteChartOpen = ref(false);

/* ----------------------------- */
/* 현재 활성화된 종목 코드 */
/* ----------------------------- */
const activeCode = computed(() => {
  if (searchChartOpen.value && searchSelectedStock.value?.code) {
    return searchSelectedStock.value.code;
  }
  if (favoriteChartOpen.value && favoriteSelectedStock.value?.code) {
    return favoriteSelectedStock.value.code;
  }
  return null;
});

/* ----------------------------- */
/* watch */
/* ----------------------------- */

/* 관심종목 삭제 시 차트 닫기 */
watch(
  () => store.favorites,
  (newFavorites) => {
    if (
      favoriteSelectedStock.value &&
      !newFavorites.some(
        f => f.stock === favoriteSelectedStock.value.code
      )
    ) {
      favoriteSelectedStock.value = null;
      favoriteChartOpen.value = false;
    }
  }
);

/* WebSocket 연결 제어 */
watch(activeCode, (code) => {
  if (code) {
    chartSocketStore.connect(code);
  } else {
    chartSocketStore.disconnect();
  }
});

/* ----------------------------- */
/* mounted */
/* ----------------------------- */
onMounted(async () => {
  const hasToken = !!localStorage.getItem("accessToken");

  if (hasToken) {
    await Promise.all([
      store.fetchWatchlist(),
      alertsStore.fetchAlerts(),
    ]);
  } else {
    store.loadFromLocal();
  }

  try {
    const res = await api.get("/stocks/");
    stocks.value = res.data.map((s) => ({
      code: s.stock_id,
      stockId: s.stock_id,
      name: s.stock_name,
      marketType: s.market_type,
      price: 0,
      change: 0,
      changeRate: 0,
    }));
  } catch (err) {
    console.error("stocks 조회 실패", err);
  }
});

/* ----------------------------- */
/* computed */
/* ----------------------------- */
const filteredStocks = computed(() => {
  if (!searchKeyword.value) return stocks.value;
  return stocks.value.filter(
    s => s.name?.includes(searchKeyword.value)
      || s.code?.includes(searchKeyword.value)
  );
});

const favoriteStocks = computed(() => {
  return store.favorites
    .map(f => stocks.value.find(s => s.code === f.stock))
    .filter(Boolean);
});

/* ----------------------------- */
/* event handlers */
/* ----------------------------- */
function onSearch(keyword) {
  searchKeyword.value = keyword;
}

function onSelectFromSearch(stock) {
  if (searchSelectedStock.value?.code === stock.code) {
    searchChartOpen.value = !searchChartOpen.value;
    return;
  }
  searchSelectedStock.value = { ...stock };
  searchChartOpen.value = true;
}

function onSelectFromFavorite(stock) {
  if (favoriteSelectedStock.value?.code === stock.code) {
    favoriteChartOpen.value = !favoriteChartOpen.value;
    return;
  }
  favoriteSelectedStock.value = { ...stock };
  favoriteChartOpen.value = true;
}

function updateSearchStockPrice(payload) {
  if (!searchSelectedStock.value) return;
  Object.assign(searchSelectedStock.value, payload);
}

function updateFavoriteStockPrice(payload) {
  if (!favoriteSelectedStock.value) return;
  Object.assign(favoriteSelectedStock.value, payload);
}
</script>


<style scoped>
.page-container {
  width: 100%;
  display: grid;

  /* 🔧 핵심: grid overflow 방지 */
  grid-template-columns: minmax(0, 3fr) minmax(0, 1.2fr);
  gap: 20px;
  align-items: start;
}

.left-column {
  display: flex;
  flex-direction: column;
}

.right-column {
  margin-left: 24px;
  min-width: 0;

  /* ⭐ 추가 */
  display: flex;
  flex-direction: column;
  gap: 16px;

}


/* 🔍 검색 결과 */
.search-results {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

/* ⭐ 관심종목 영역 */
.favorite-section {
  margin-top: 8px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 📈 차트 카드 */
.chart-box {
  margin-top: 24px;
  padding: 24px;
  width: 100%;
  max-width: 100%;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-sizing: border-box;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* 📱 반응형 */
@media (max-width: 1024px) {
  .page-container {
    grid-template-columns: 1fr;
  }
}
.search-bar-wrapper {
  margin-bottom: 8px; /* ← 여기서 간격 조절 */
}

</style>
