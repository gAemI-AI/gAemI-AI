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
          v-for="item in favorites"
          :key="item.code"
          class="favorite-item-box"
        >
          <div class="favorite-info">
            <span class="favorite-name">{{ item.name }}</span>
            <span class="favorite-code">({{ item.code }})</span>
          </div>

          <!-- 삭제 버튼 통일 -->
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
      <AlertForm :stocks="favorites" @create="addAlert" />

      <!-- 알림 리스트 -->
      <AlertList :items="alerts" @remove="removeAlert" />
    </section>

  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";

import AlertForm from "@/components/alerts/AlertForm.vue";
import AlertList from "@/components/alerts/AlertList.vue";

/* -------------------------------------------------- */
/* Pinia 관심종목 store */
/* -------------------------------------------------- */
const store = useFavoritesStore();
const favorites = computed(() => store.favorites);

/* -------------------------------------------------- */
/* 알림 목록 상태 */
/* -------------------------------------------------- */
const alerts = ref([
  { id: 1, stock: "005930", stockName: "삼성전자", enabled: true, description: "이상: 80,000원" },
  { id: 2, stock: "000660", stockName: "SK하이닉스", enabled: true, description: "이하: 130,000원" }
]);

/* -------------------------------------------------- */
/* 관심종목 삭제 */
/* -------------------------------------------------- */
function removeFavorite(code) {
  store.removeFavorite(code);
}

/* -------------------------------------------------- */
/* 알림 추가 */
/* -------------------------------------------------- */
function addAlert(alert) {
  alerts.value.push({
    id: Date.now(),
    ...alert
  });
}

/* -------------------------------------------------- */
/* 알림 삭제 */
/* -------------------------------------------------- */
function removeAlert(id) {
  alerts.value = alerts.value.filter((a) => a.id !== id);
}
</script>

<style scoped>
.settings-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 전체 박스를 감싸는 컨테이너 */
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


/* ============================ */
/* 관심종목 UI */
/* ============================ */

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

.favorite-info {
  font-weight: 600;
}

.favorite-code {
  color: #9ca3af;
  margin-left: 4px;
}

/* 휴지통 버튼 통일 */
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
