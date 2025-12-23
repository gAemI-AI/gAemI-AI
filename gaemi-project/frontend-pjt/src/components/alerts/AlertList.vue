<template>
  <div class="panel">
    <header class="header">
      <span>활성 알림 ({{ items.length }})</span>
    </header>

    <!-- 알림 없을 때 -->
    <p v-if="items.length === 0" class="empty">
      등록된 알림이 없습니다.
    </p>

    <!-- 알림 목록 -->
    <div v-else class="list">
      <div v-for="item in items" :key="item.id" class="row">
        <div class="info">
          <div class="name">{{ item.stockName }}</div>
          <div class="condition">{{ item.title }}</div>
        </div>
        <div class="actions">
          <!-- <label class="toggle">
            <input
              type="checkbox"
              v-model="item.enabled"
              @change="$emit('toggle', item)"
            />
            <span class="slider"></span>
          </label> -->
          <span class="status">🟢</span>
          <button class="delete" @click="$emit('remove', item.id)">🗑️</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
});
defineEmits(["remove"]);
</script>

<style scoped>
.panel {
  background: white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}
.header {
  font-size: 14px;
  margin-bottom: 10px;
}
.empty {
  font-size: 13px;
  color: #9ca3af;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.name {
  font-size: 14px;
  font-weight: 600;
}
.condition {
  font-size: 12px;
  color: #6b7280;
}
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.delete {
  border: none;
  background: transparent;
  cursor: pointer;
}

/* 토글 */
.toggle {
  position: relative;
  display: inline-block;
  width: 34px;
  height: 18px;
}
.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: #d1d5db;
  border-radius: 999px;
  transition: 0.2s;
}
.slider::before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: 0.2s;
}
.toggle input:checked + .slider {
  background-color: #2563eb;
}
.toggle input:checked + .slider::before {
  transform: translateX(16px);
}
</style>
