<!-- src/pages/DashboardPage.vue -->
<template>
  <div class="page-container">

    <!-- --------------------------------------- -->
    <!-- 🔍 검색창 -->
    <!-- --------------------------------------- -->
    <section class="left-column">
      <StockSearchBar @search="onSearch" />

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
      <AlertHistoryList :alerts="alerts" />
    </aside>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";

import StockSearchBar from "@/components/dashboard/StockSearchBar.vue";
import StockTickerRow from "@/components/dashboard/StockTickerRow.vue";
import StockDetailCard from "@/components/dashboard/StockDetailCard.vue";
import AlertHistoryList from "@/components/dashboard/AlertHistoryList.vue";
import FavoriteButton from "@/components/common/FavoriteButton.vue";

/* Pinia Store */
const store = useFavoritesStore();

/* ------------------------------- */
/* 로그인 유저 관심종목 불러오기   */
/* ------------------------------- */
onMounted(() => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (user?.favorites) {
    store.loadFavorites(user.favorites); // ⭐ Pinia에 로드
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

/* -------------------------------------- */
/* 더미 종목 데이터 */
/* -------------------------------------- */
const stocks = [
  { code: '005930', name: '삼성전자', price: 70680, change: -1320, changeRate: -1.83 },
  { code: '000660', name: 'SK하이닉스', price: 139421, change: 579, changeRate: 0.41 },
  { code: '035420', name: 'NAVER', price: 215222, change: 3722, changeRate: 1.76 },
  { code: '006400', name: '삼성SDI', price: 386519, change: -6481, changeRate: -1.65 },
  { code: '005380', name: '현대차', price: 195740, change: 3240, changeRate: 1.68 }
];

/* -------------------------------------- */
/* 검색 결과 필터링 */
/* -------------------------------------- */
const filteredStocks = computed(() => {
  if (!searchKeyword.value) return stocks;
  return stocks.filter(
    (s) =>
      s.name.includes(searchKeyword.value) ||
      s.code.includes(searchKeyword.value)
  );
});

/* 관심종목 리스트 */
const favoriteStocks = computed(() => store.favorites);

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
  grid-template-columns: 3fr 1.2fr;
  gap: 20px;
}

.left-column {
  display: flex;
  flex-direction: column;
}

.search-results {
  margin-top: 16px;
}

.favorite-section {
  margin-top: 24px;
}

.chart-box {
  margin-top: 24px;
  padding: 24px;
  width: 100%;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.right-column {
  min-width: 280px;
}

@media (max-width: 1024px) {
  .page-container {
    grid-template-columns: 1fr;
  }
}
</style>
