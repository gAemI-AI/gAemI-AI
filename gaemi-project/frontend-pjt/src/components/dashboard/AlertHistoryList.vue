<template>
  <div class="alert-list-container">
    <div class="list">
      <div v-if="alerts.length === 0" class="empty-state">
        <span class="empty-icon">🔕</span>
        <p class="empty-text">설정된 알림 조건이 없습니다</p>
      </div>

      <div 
        v-for="(alert, index) in alerts" 
        :key="alert.id || index" 
        class="item" 
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <div class="item-left">
          <div class="status-badge active">
            <span class="status-icon">●</span>
            <span class="status-text">{{ alert.stockName || alert.stock_name || alert.stockCode || alert.code }}</span>
          </div>
        </div>
        
        <div class="item-content">
          <p class="item-title">
            {{ (alert.condition === 'gte' || alert.conditionType === 'PRICE_ABOVE') ? '목표가 이상' : 
               (alert.condition === 'lte' || alert.conditionType === 'PRICE_BELOW') ? '목표가 이하' : '가격 알림' }} 
            
            <span class="price-highlight">
              {{ Number(alert.target || alert.targetPrice || 0).toLocaleString() }}원
            </span>
          </p>
          <p class="item-time">
            {{ formatDate(alert.createdAt || alert.created_at || new Date()) }} 설정
          </p>
        </div>

        </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  alerts: { type: Array, required: true, default: () => [] },
});

// defineEmits(['delete']); // 이것도 필요 없으므로 삭제 가능

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}
</script>

<style scoped>
/* ======================= */
/* 스타일 (기존과 동일) */
/* ======================= */
.alert-list-container {
  width: 100%; height: 100%; background: transparent; border: none; padding: 0; 
  display: flex; flex-direction: column;
}

.list {
  display: flex; flex-direction: column; gap: 10px; overflow-y: auto;
  max-height: 320px; padding-right: 4px;
}
.list::-webkit-scrollbar { width: 4px; }
.list::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }

.item {
  display: flex; align-items: center; gap: 12px; padding: 12px 14px;
  border-radius: 12px; background: #f9fafb; border: 1px solid #f3f4f6;
  animation: slideIn 0.3s ease-out backwards; transition: all 0.2s ease;
}
.item:hover { background: #f3f4f6; border-color: #e5e7eb; }

@keyframes slideIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.item-left { flex-shrink: 0; }

.status-badge {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px;
  font-size: 11px; font-weight: 700; background: white; border: 1px solid #e5e7eb; color: #374151;
}
.status-badge.active { color: #2563eb; border-color: #dbeafe; background: #eff6ff; }
.status-icon { font-size: 6px; color: #2563eb; }

.item-content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }

.item-title {
  font-size: 13px; font-weight: 500; color: #4b5563; margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.price-highlight { font-weight: 700; color: #111827; margin-left: 4px; }

.item-time { font-size: 11px; color: #9ca3af; margin: 0; }

/* delete-btn 스타일 제거 */

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 40px 0; color: #9ca3af; border: 1px dashed #e5e7eb; border-radius: 12px;
}
.empty-icon { font-size: 24px; margin-bottom: 8px; opacity: 0.6; }
.empty-text { font-size: 13px; margin: 0; }
</style>