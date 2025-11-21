<template>
  <div class="alert-panel">
    <header class="header">
      <span>알림 내역</span>
      <span class="count">{{ alerts.length }}개</span>
    </header>

    <div class="list">
      <div v-for="alert in alerts" :key="alert.id" class="item">
        <div class="left">
          <div class="badge" :class="alert.statusClass">{{ alert.stockName }}</div>
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
  height: 100%;
  display: flex;
  flex-direction: column;
}
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}
.count {
  color: #9ca3af;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
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
