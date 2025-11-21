<template>
  <div class="ticker-row">
    <div
      v-for="stock in stocks"
      :key="stock.code"
      class="ticker-card"
      :class="{ selected: stock.code === selectedCode }"
      @click="$emit('select', stock)"
    >
      <div class="code">{{ stock.code }}</div>
      <div class="name">{{ stock.name }}</div>
      <div class="price">{{ stock.price.toLocaleString() }}원</div>
      <div
        class="change"
        :class="{ up: stock.change > 0, down: stock.change < 0 }"
      >
        {{ stock.change > 0 ? '+' : '' }}{{ stock.change.toLocaleString() }}원
        ({{ stock.changeRate.toFixed(2) }}%)
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stocks: { type: Array, required: true },
  selectedCode: { type: String, default: null },
});
defineEmits(['select']);
</script>

<style scoped>
.ticker-row {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.ticker-card {
  min-width: 180px;
  background: white;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
}

.ticker-card.selected {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px #2563eb22;
}

.code {
  font-size: 12px;
  color: #9ca3af;
}
.name {
  font-weight: 600;
  margin-top: 4px;
}
.price {
  margin-top: 4px;
  font-size: 16px;
  font-weight: 600;
}
.change {
  margin-top: 2px;
  font-size: 12px;
}
.change.up {
  color: #ef4444;
}
.change.down {
  color: #2563eb;
}
</style>
