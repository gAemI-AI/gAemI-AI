<template>
  <div class="news-list">
    <div v-for="item in items" :key="item.id" class="card">
      <div class="top-row">
        <span class="badge stock">{{ item.stock }}</span>
        <span class="badge sentiment" :class="item.sentimentClass">
          {{ item.sentimentLabel }}
        </span>
        <span class="badge type">{{ item.type }}</span>
      </div>
      <div class="title">{{ item.title }}</div>
      <div class="summary">{{ item.summary }}</div>
      <div class="bottom-row">
        <span class="source">{{ item.source }}</span>
        <span class="time">{{ item.time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
});
</script>

<style scoped>
.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}
.top-row {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 11px;
}
.badge {
  border-radius: 999px;
  padding: 2px 8px;
  background: #f3f4f6;
}
.badge.stock {
  font-weight: 600;
}
.badge.sentiment.positive {
  background: #dcfce7;
  color: #166534;
}
.badge.sentiment.negative {
  background: #fee2e2;
  color: #b91c1c;
}
.title {
  font-weight: 600;
  margin-bottom: 4px;
}
.summary {
  font-size: 13px;
  color: #4b5563;
}
.bottom-row {
  margin-top: 8px;
  font-size: 11px;
  color: #9ca3af;
  display: flex;
  justify-content: space-between;
}
</style>
