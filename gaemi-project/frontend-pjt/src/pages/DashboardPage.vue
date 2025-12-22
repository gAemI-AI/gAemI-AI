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
        <StockDetailCard :stock="searchSelectedStock" />
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
        <StockDetailCard :stock="favoriteSelectedStock" />
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
import { ref, computed, onMounted } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";
import { useAlertsStore } from "@/stores/alertsStore";
import api from "@/api/axios";
import StockSearchBar from "@/components/dashboard/StockSearchBar.vue";
import StockTickerRow from "@/components/dashboard/StockTickerRow.vue";
import StockDetailCard from "@/components/dashboard/StockDetailCard.vue";
import AlertHistoryList from "@/components/dashboard/AlertHistoryList.vue";
import FavoriteButton from "@/components/common/FavoriteButton.vue";
import MarketSummaryPanel from "@/components/dashboard/MarketSummaryPanel.vue";

/* Pinia Store */
const store = useFavoritesStore();

// // 🔔 더미 알림 데이터 추가
// const alerts = ref([
//   {
//     id: 1,
//     statusClass: "working",
//     stockName: "삼성전자",
//     title: "목표가 도달했습니다.",
//     time: "10:32",
//   },
//   {
//     id: 2,
//     statusClass: "done",
//     stockName: "NAVER",
//     title: "지정가 이하로 하락했습니다.",
//     time: "09:15",
//   },
// ]);
const alertsStore = useAlertsStore();

/* ------------------------------- */
/* 로그인 유저 관심종목 불러오기   */
/* ------------------------------- */
onMounted(async () => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (user?.favorites) {
    store.loadFavorites(user.favorites); // ⭐ Pinia에 로드
  }

  try {
    const res = await api.get("/stocks/");
    stocks.value = res.data.map((s) => ({
      code: s.stock_id,
      name: s.stock_name,
      marketType: s.market_type,

      price: 0,
      change: 0,
      changeRate: 0,
    }));
    console.log("[stocks]", res.data);
  } catch (err) {
    console.error('stocks 조회 실패', err);
  }
});

/* -------------------------------------- */
/* 검색 관련 상태 */
/* -------------------------------------- */
const searchKeyword = ref("");
const searchSelectedStock = ref(null);
const searchChartOpen = ref(false);

/* -------------------------------------- */
/* 관심종목 상태 */
/* -------------------------------------- */
const favoriteSelectedStock = ref(null);
const favoriteChartOpen = ref(false);
const stocks = ref([]);
/* -------------------------------------- */
/* 검색 결과 필터링 */
/* -------------------------------------- */
const filteredStocks = computed(() => {
  if (!searchKeyword.value) return stocks.value;
  return stocks.value.filter(
    (s) =>
      s.name.includes(searchKeyword.value) ||
      s.code.includes(searchKeyword.value)
  );
});

/* 관심종목 리스트 */
// const favoriteStocks = computed(() => store.favorites);
const favoriteStocks = computed(() =>
  store.favorites
    .map(code => stocks.value.find(s => s.code === code))
    .filter(Boolean)
);



/* 이벤트 */
function onSearch(keyword) {
  searchKeyword.value = keyword;
}

function onSelectFromSearch(stock) {
  if (searchSelectedStock.value?.code === stock.code) {
    searchChartOpen.value = !searchChartOpen.value;
  } else {
    searchSelectedStock.value = stock;
    searchChartOpen.value = true;
  }
}

function onSelectFromFavorite(stock) {
  if (favoriteSelectedStock.value?.code === stock.code) {
    favoriteChartOpen.value = !favoriteChartOpen.value;
  } else {
    favoriteSelectedStock.value = stock;
    favoriteChartOpen.value = true;
  }
}
</script>

<style scoped>
.page-container {
  width: 100%;
  display: grid;

  /* 🔧 핵심: grid overflow 방지 */
  grid-template-columns: minmax(0, 3fr) minmax(0, 1.2fr);
  gap: 20px;
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

  /* 오른쪽 컬럼 자체는 스크롤 ❌ */
  height: calc(100vh - 64px - 40px); 
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
