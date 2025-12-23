<!-- src/pages/AlertSettingsPage.vue -->
<template>
  <div class="settings-page">

    <!-- ================================ -->
    <!-- 📌 관심 종목 관리 -->
    <!-- ================================ -->
    <section class="section-box">
      <h2 class="section-title">관심 종목 관리</h2>

      <div class="favorite-container">
        <div
          v-for="item in favoriteStocks"
          :key="item.code"
          class="favorite-item-box"
        >
          <div class="favorite-info">
            <!-- 이름 출력 -->
            <span class="favorite-name">{{ item.name }}</span>
            <!-- 코드가 있을 때만 괄호 출력 -->
            <span
              v-if="item.code"
              class="favorite-code"
            >
              ({{ item.code }})
            </span>
          </div>

          <!-- 삭제 버튼 -->
          <button class="icon-btn" @click="removeFavorite(item.code)">🗑️</button>
        </div>
      </div>
    </section>

    <!-- ================================ -->
    <!-- 🔔 알림 조건 관리 -->
    <!-- ================================ -->
    <section class="section-box">
      <h2 class="section-title">알림 조건 관리</h2>

      <!-- 알림 생성 폼 -->
      <AlertForm :stocks="favoriteStocks" @create="addAlert" />

      <!-- 활성 알림 리스트 -->
      <AlertList
        :items="alertItems"
        @remove="removeAlert"
      />

    </section>

  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";
import { useAlertsStore } from "@/stores/alertsStore.js";
import AlertForm from "@/components/alerts/AlertForm.vue";
import AlertList from "@/components/alerts/AlertList.vue";

/* 관심 종목 store */
const favoritesStore = useFavoritesStore();
const alertsStore = useAlertsStore();
// const alertEvents = computed(() => alertsStore.alertEvents);

/* 관심 종목 */
const favoriteStocks = computed(() =>
  favoritesStore.favorites.map(f => ({
    code: f.stock,
    name: f.stock_details?.stock_name ?? f.stock,
  }))
);

const alertItems = computed(() => 
  alertsStore.alertEvents.map(a => {
    const stock = favoriteStocks.value.find(s => s.code === a.stockCode);

    return {
      ...a,
      stockName: stock?.name || a.stockName || a.stockCode,
    };
  })
);

onMounted(async () => {
  await favoritesStore.fetchWatchlist();
  await alertsStore.fetchAlerts();
});

/* 알림 생성 */
function addAlert(alert) {
  alertsStore.addAlert({
    stockCode: alert.stock,
    condition: alert.condition,
    target: alert.target,
  });
}

/* 알림 삭제 */
function removeAlert(id) {
  alertsStore.removeAlert(id);
}

/* 관심 종목 삭제 */
async function removeFavorite(code) {
  if (alertsStore.hasAlertsForStock(code)) {
    const ok = confirm(
      "관심 종목을 삭제하면 해당 종목의 알림 조건도 함께 삭제됩니다.\n계속하시겠습니까?"
    );
    if (!ok) return;

    await alertsStore.removeByStockCode(code);
  }
  await favoritesStore.removeFavorite(code);
  await favoritesStore.fetchWatchlist();
}
</script>


<style scoped>
.settings-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 30px 20px;
}

.section-box {
  background: white;
  padding: 24px;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  margin-bottom: 28px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
}

/* 관심종목 */
.favorite-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.favorite-item-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.favorite-name {
  font-weight: 600;
}

.favorite-code {
  color: #9ca3af;
  margin-left: 4px;
}

.icon-btn {
  border: none;
  background: none;
  cursor: pointer;
  color: #6b7280;
  font-size: 18px;
  padding: 6px;
  border-radius: 6px;
}
.icon-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}
</style>
