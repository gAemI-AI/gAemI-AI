<template>
  <div class="page-container">

    <section class="left-column">
      <div class='search-bar-wrapper'>
        <StockSearchBar @search="onSearch" />
      </div>

      <section v-if="searchKeyword" class="search-section">
        <div class="section-header">
          <h2>검색 결과</h2>
          <span class="result-count">{{ filteredStocks.length }}개</span>
        </div>
        
        <div v-if="filteredStocks.length > 0" class="search-results">
          <StockTickerRow
            :stocks="filteredStocks"
            :selected-code="searchSelectedStock?.code"
            @select="onSelectFromSearch"
          />
        </div>
        
        <div v-else class="empty-state">
          <p class="empty-text">검색 결과가 없습니다</p>
        </div>
      </section>

      <div v-if="searchChartOpen && searchSelectedStock" class="chart-box">
        <div class="chart-header">
          <h3>{{ searchSelectedStock.name }} ({{ searchSelectedStock.code }})</h3>
          <FavoriteButton :stock="searchSelectedStock" />
        </div>
        
        <StockDetailCard
          :stock="searchSelectedStock"
          @updatePrice="updateSearchStockPrice"
        />

        <StockNewsList :stock-code="searchSelectedStock.code" />
      </div>

      <div class="favorite-section">
        <div class="section-header">
          <h2>내 관심종목</h2>
        </div>

        <div v-if="favoriteStocks.length > 0" class="favorite-list">
          <StockTickerRow
            :stocks="favoriteStocks"
            :selected-code="favoriteSelectedStock?.code"
            @select="onSelectFromFavorite"
          />
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">⭐</div>
          <p class="empty-text">관심 종목을 등록해보세요</p>
          <p class="empty-subtext">검색해서 별을 눌러 관심 종목을 추가할 수 있습니다</p>
        </div>
      </div>

      <div v-if="favoriteChartOpen && favoriteSelectedStock" class="chart-box">
        <div class="chart-header">
          <h3>{{ favoriteSelectedStock.name }} ({{ favoriteSelectedStock.code }})</h3>
          <FavoriteButton :stock="favoriteSelectedStock" />
        </div>
        
        <StockDetailCard
          :stock="favoriteSelectedStock"
          @updatePrice="updateFavoriteStockPrice"
        />

        <StockNewsList :stock-code="favoriteSelectedStock.code" />
      </div>
    </section>

    <aside class="right-column">
      
      <MarketSummaryPanel />
      
      <div class="panel-box">
        <div class="panel-header">
          <h3 class="panel-title">알림 조건 목록</h3>
          <span class="count-badge">{{ alertsStore.alerts.length }}</span>
        </div>
        <AlertHistoryList :alerts="alertsStore.alertEvents" />
      </div>

      <WeeklyReportList />
      
    </aside>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from "vue";
import api from "@/api/axios";

/* components */
import StockSearchBar from "@/components/dashboard/StockSearchBar.vue";
import StockTickerRow from "@/components/dashboard/StockTickerRow.vue";
import StockDetailCard from "@/components/dashboard/StockDetailCard.vue";
import AlertHistoryList from "@/components/dashboard/AlertHistoryList.vue";
import FavoriteButton from "@/components/common/FavoriteButton.vue";
import MarketSummaryPanel from "@/components/dashboard/MarketSummaryPanel.vue";
import StockNewsList from "@/components/dashboard/StockNewsList.vue"; 
import WeeklyReportList from "@/components/dashboard/WeeklyReportList.vue"; 

/* services */
import websocketService from "@/services/websocketService";

/* stores */
import { useFavoritesStore } from "@/stores/favoritesStore";
import { useAlertsStore } from "@/stores/alertsStore";
import { useToastStore } from "@/stores/toastStore";

const store = useFavoritesStore();
const alertsStore = useAlertsStore();
const toastStore = useToastStore();

/* 상태 정의 */
const stocks = ref([]);
const unsubscribeFunctions = ref([]);

/* 검색 관련 상태 */
const searchKeyword = ref("");
const searchSelectedStock = ref(null);
const searchChartOpen = ref(false);

/* 관심종목 관련 상태 */
const favoriteSelectedStock = ref(null);
const favoriteChartOpen = ref(false);

/* Watchers */
watch(
  () => store.favorites,
  (newFavorites) => {
    if (
      favoriteSelectedStock.value &&
      !newFavorites.includes(favoriteSelectedStock.value.code)
    ) {
      favoriteSelectedStock.value = null;
      favoriteChartOpen.value = false;
    }
  }
);

/* WebSocket 알림 구독 */
const subscribeToNotifications = async () => {
  // localStorage에서 user 객체 가져오기
  const userStr = localStorage.getItem("user");
  const user = userStr ? JSON.parse(userStr) : null;
  const userId = user?.id;
  
  if (!userId) {
    console.warn("사용자 ID가 없어 알림 구독을 건너뜁니다.");
    return;
  }

  try {
    const unsubscribe = await websocketService.subscribeNotifications(
      userId,
      (message) => {
        if (message.type === 'alert') {
          // 알림 데이터 처리
          console.log('받은 알림:', message.data);
          
          // 토스트 메시지 표시
          toastStore.add({
            type: 'info',
            title: '📢 알림',
            message: message.data,
            duration: 8000,
          });
        }
      }
    );
    
    unsubscribeFunctions.value.push(unsubscribe);
  } catch (err) {
    console.error(`알림 구독 실패:`, err);
  }
};

/* Lifecycle Hooks */
onMounted(async () => {
  const hasToken = !!localStorage.getItem("accessToken");

  if (hasToken) {
    await Promise.all([
      store.fetchWatchlist(),
      alertsStore.fetchAlerts(),
    ]);
    
    // WebSocket 알림 구독
    subscribeToNotifications();
  } else {
    store.loadFromLocal();
  }

  try {
    const response = await api.get("/stocks/");
    stocks.value = response.data.map((s) => ({
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

// 컴포넌트 언마운트 시 모든 WebSocket 구독 해제
onUnmounted(() => {
  unsubscribeFunctions.value.forEach(unsub => unsub());
  unsubscribeFunctions.value = [];
});

/* Computed Properties */
const filteredStocks = computed(() => {
  if (!searchKeyword.value) return stocks.value;
  return stocks.value.filter(
    s => s.name?.includes(searchKeyword.value)
      || s.code?.includes(searchKeyword.value)
  );
});

const favoriteStocks = computed(() => {
  return store.favorites
    .map(code => stocks.value.find(s => s.code === code))
    .filter(Boolean);
});

/* Event Handlers */
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
/* ======================= */
/* 레이아웃 */
/* ======================= */
.page-container {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1.2fr);
  gap: 32px;
  align-items: start;
  padding: 0;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px; /* 패널 사이 간격 */
  position: sticky;
  top: 80px;
}

/* ======================= */
/* 공통 패널 박스 스타일 (우측 컬럼 통일) */
/* ======================= */
.panel-box {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #191f28;
  margin: 0;
}

.count-badge {
  background: #f2f4f6;
  color: #6b7684;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

/* ======================= */
/* 섹션 헤더 (왼쪽 컬럼용) */
/* ======================= */
.section-header {
  margin-bottom: 16px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  letter-spacing: -0.4px;
}

.result-count {
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  background: rgba(37, 99, 235, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
}

/* ======================= */
/* 검색 섹션 */
/* ======================= */
.search-bar-wrapper {
  margin-bottom: 0;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(59, 130, 246, 0.03) 100%);
  border: 1px solid #dbeafe;
  border-radius: 16px;
  margin-bottom: 8px;
}

.search-results {
  position: relative;
  z-index: 30;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 480px;
  overflow-y: auto;
  scroll-behavior: smooth;
  padding: 0 8px 0 0;
}

.search-results::-webkit-scrollbar { width: 6px; }
.search-results::-webkit-scrollbar-thumb { background: rgba(0, 0, 0, 0.2); border-radius: 3px; }
.search-results::-webkit-scrollbar-thumb:hover { background: rgba(0, 0, 0, 0.3); }

/* ======================= */
/* 관심종목 섹션 */
/* ======================= */
.favorite-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0;
}

/* ======================= */
/* 차트 박스 */
/* ======================= */
.chart-box {
  margin-top: 16px;
  padding: 24px;
  width: 100%;
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-sizing: border-box;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

/* ======================= */
/* 빈 상태 (Empty State) */
/* ======================= */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  text-align: center;
  background: #f9fafb;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
}

.empty-icon { font-size: 48px; margin-bottom: 16px; display: block; }
.empty-text { font-size: 16px; font-weight: 600; color: #111827; margin: 0 0 8px 0; }
.empty-subtext { font-size: 14px; color: #6b7280; margin: 0; }

/* ======================= */
/* 반응형 */
/* ======================= */
@media (max-width: 1024px) {
  .page-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .right-column {
    position: static;
    gap: 20px;
  }
}

@media (max-width: 640px) {
  .chart-box { padding: 16px; }
  .empty-state { padding: 40px 24px; }
}
</style>