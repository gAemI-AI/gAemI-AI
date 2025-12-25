<template>
  <div class="alert-list-container">
    <div class="list-header">
      <h3>등록된 알림 <span class="count">{{ items.length }}</span></h3>
    </div>

    <div v-if="items.length === 0" class="empty-list">
      <div class="icon">🔕</div>
      <p>아직 등록된 알림이 없어요</p>
    </div>

    <div v-else class="list-items">
      <div 
        v-for="item in items" 
        :key="item.id" 
        class="alert-card"
        :class="{ disabled: !item.enabled }"
      >
        <div class="card-info">
          <div class="top-row">
            <span class="stock-name">{{ item.stockName }}</span>
            <span class="stock-code">{{ item.stockCode }}</span>
          </div>
          <div class="condition-text">
            {{ item.description }}
          </div>
        </div>

        <div class="card-actions">
          <label class="switch">
            <input 
              type="checkbox" 
              v-model="item.enabled"
              @change="$emit('toggle', item)"
            >
            <span class="slider round"></span>
          </label>
          
          <button class="delete-icon" @click="$emit('remove', item.id)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
});
defineEmits(["toggle", "remove"]);
</script>

<style scoped>
.alert-list-container {
  margin-top: 10px;
}

.list-header {
  margin-bottom: 16px;
}

.list-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.count {
  color: #3182f6;
  margin-left: 4px;
}

/* 비었을 때 */
.empty-list {
  text-align: center;
  padding: 40px 0;
  color: #adb5bd;
}

.empty-list .icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
}

/* 리스트 아이템 */
.list-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-card {
  background: white;
  border: 1px solid #e5e8eb;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.alert-card:hover {
  border-color: #d1d6db;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.alert-card.disabled {
  opacity: 0.6;
  background: #f9fafb;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.top-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stock-name {
  font-weight: 700;
  font-size: 16px;
  color: #333;
}

.stock-code {
  font-size: 12px;
  color: #8b95a1;
  background: #f2f4f6;
  padding: 2px 6px;
  border-radius: 6px;
}

.condition-text {
  font-size: 14px;
  color: #4e5968;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.delete-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #adb5bd;
  transition: color 0.2s;
  padding: 4px;
}

.delete-icon:hover {
  color: #ef4444;
}

/* --- 토글 스위치 (iOS Style) --- */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e8eb;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #3182f6;
}

input:checked + .slider:before {
  transform: translateX(20px);
}
</style>