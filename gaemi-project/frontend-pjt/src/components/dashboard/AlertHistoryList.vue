<template>
  <div class="alert-panel">
    <header class="panel-header">
      <h3 class="header-title">알림 조건 목록</h3>
      <span class="badge-count">{{ alerts.length }}</span>
    </header>

    <div class="list">
      <div v-if="alerts.length === 0" class="empty-state">
        <span class="empty-icon">🔔</span>
        <p class="empty-text">설정된 알림이 없습니다</p>
      </div>

      <div 
        v-for="(alert, index) in alerts" 
        :key="alert.id || index" 
        class="item" 
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <div class="item-left">
          <div class="status-badge" :class="alert.statusClass || 'active'">
            <span class="status-icon">●</span>
            <span class="status-text">{{ alert.stockName }}</span>
          </div>
        </div>
        
        <div class="item-content">
          <p class="item-title">{{ alert.title }}</p>
          <p class="item-time">{{ alert.time }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// router 관련 로직 모두 삭제
defineProps({
  alerts: { type: Array, required: true, default: () => [] },
});
</script>

<style scoped>
/* ======================= */
/* 알림 패널         */
/* ======================= */
.alert-panel {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 280px;
}

/* ======================= */
/* 패널 헤더         */
/* ======================= */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  letter-spacing: -0.3px;
}

.badge-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* ======================= */
/* 리스트            */
/* ======================= */
.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  max-height: 400px;
  padding-right: 8px;
}

.list::-webkit-scrollbar {
  width: 6px;
}

.list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* ======================= */
/* 빈 상태           */
/* ======================= */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.empty-text {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}

/* ======================= */
/* 아이템            */
/* ======================= */
.item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  /* transition 및 cursor 제거 */
  animation: slideIn 0.3s ease-out backwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* hover 시 움직임 효과 제거 (색상만 살짝 변경) */
.item:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

/* ======================= */
/* 상태 배지 (가독성 개선) */
/* ======================= */
.item-left {
  flex-shrink: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

.status-text {
  font-weight: 700;
  color: inherit;
}

.status-badge.active {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #dbeafe;
}

.status-badge.warning {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fcd34d;
}

.status-badge.critical {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}

.status-badge.success {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #6ee7b7;
}

.status-icon {
  font-size: 8px;
}

/* ======================= */
/* 아이템 콘텐츠     */
/* ======================= */
.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
  letter-spacing: -0.2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-time {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

/* ======================= */
/* 반응형            */
/* ======================= */
@media (max-width: 640px) {
  .alert-panel {
    padding: 16px;
    min-height: 250px;
  }
}
</style>