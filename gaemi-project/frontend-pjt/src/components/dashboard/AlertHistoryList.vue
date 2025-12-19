<template>
  <div class="alert-panel">
    <header class="header">
      <span>알림 조건 목록</span>
      <span class="count">{{ alerts.length }}개</span>
    </header>

    <!-- 🔔 스크롤은 여기만 -->
    <div class="list">
      <div v-for="alert in alerts" :key="alert.id" class="item">
        <div class="left">
          <div class="badge" :class="alert.statusClass">
            {{ alert.stockName }}
          </div>
          <div class="title">{{ alert.title }}</div>
          <div class="time">{{ alert.time }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  alerts: { type: Array, required: true },
});
</script>

<style scoped>
.alert-panel {
  background: white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;

  /* ⭐ 핵심 */
  display: flex;
  flex-direction: column;
}

/* 헤더는 고정 */
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.count {
  color: #9ca3af;
}

/* 🔥 스크롤 영역 */
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;

  /* ⭐ 여기만 스크롤 */
  overflow-y: auto;
  max-height: 360px; /* ← 원하는 높이로 조절 */
  padding-right: 4px;
}

/* 아이템 */
.item {
  padding: 10px 12px;
  border-radius: 10px;
  background: #f9fafb;
}

.badge {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  margin-bottom: 4px;
  color: white;
}

.badge.working {
  background: #2563eb;
}

.title {
  font-size: 13px;
}

.time {
  margin-top: 2px;
  font-size: 11px;
  color: #9ca3af;
}
</style>
