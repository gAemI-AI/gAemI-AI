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
        :items="alerts"
        @remove="removeAlert"
        @toggle="toggleAlert"
      />

    </section>

  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";

import AlertForm from "@/components/alerts/AlertForm.vue";
import AlertList from "@/components/alerts/AlertList.vue";

import { onMounted } from "vue";
import { useAlertsStore } from "@/stores/alertsStore.js";


/* -------------------------------------------------- */
/* Pinia 관심종목 store */
/* -------------------------------------------------- */
const store = useFavoritesStore();

/* 더미 종목 목록 (Dashboard와 동일 구조 유지) */
const stocks = [
  { code: "005930", name: "삼성전자" },
  { code: "000660", name: "SK하이닉스" },
  { code: "035420", name: "NAVER" },
  { code: "006400", name: "삼성SDI" },
  { code: "005380", name: "현대차" },
];

const favorites = computed(() =>
  store.favorites.map(code => stocks.find(s => s.code === code)).filter(Boolean)
);
/* -------------------------------------------------- */
/* store.favorites → 실제 종목 객체로 변환 */
/* -------------------------------------------------- */
const favoriteStocks = computed(() => {
  return store.favorites
    .map((item) => {
      const code = typeof item === "string" ? item : item.code;
      return stocks.find((s) => s.code === code);
    })
    .filter((s) => s && s.name && s.code); // 빈 데이터 제거
});

/* AlertForm 전달용: 코드 배열 */
const favoriteCodes = computed(() => favoriteStocks.value.map((s) => s.code));

/* -------------------------------------------------- */
/* 활성 알림 리스트 */
/* -------------------------------------------------- */
const alertsStore = useAlertsStore();

onMounted(() => {
  alertsStore.loadFromLocal();
});

const alerts = computed(() => {
  return alertsStore.alerts.map((a) => {
    const stock = stocks.find((s) => s.code === a.stockCode);

    return {
      ...a,
      stockName: stock?.name || a.stockName || a.stockCode,
      // ✅ store에서 만든 description 그대로 사용 (덮어쓰지 않기)
      description: a.description,
    };
  });
});

function toggleAlert(item) {
  alertsStore.toggleAlert(item.id);
}


/* 삭제 */
function removeFavorite(code) {
  // 해당 종목에 연결된 알림이 있는지 확인
  const hasAlerts = alertsStore.hasAlertsForStock(code);

  if (hasAlerts) {
    const ok = confirm(
      "관심 종목을 삭제하면 해당 종목의 알림 조건도 함께 삭제됩니다.\n계속하시겠습니까?"
    );
    if (!ok) return;

    alertsStore.removeByStockCode(code);
  }

  store.removeFavorite(code);
}

function addAlert(alert) {
  const stockObj = favoriteStocks.value.find(
    s => s.code === alert.stock
  );

  alertsStore.addAlert({
    stockCode: alert.stock,
    stockName: stockObj?.name || "",
    condition: alert.condition,
    target: alert.target,
  });
}




/* 알림 삭제 */
function removeAlert(id) {
  alertsStore.removeAlert(id);
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
