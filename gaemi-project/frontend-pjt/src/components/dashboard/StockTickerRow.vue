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
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db #f3f4f6;
  position: relative;
  z-index: 20;
}

.ticker-row::-webkit-scrollbar {
  height: 6px;
}

.ticker-row::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.ticker-row::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.ticker-row::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.ticker-card {
  min-width: 160px;
  background: white;
  border-radius: 12px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  position: relative;
  z-index: 20;
}

.ticker-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
  z-index: 25;
}

.ticker-card.selected {
  border-color: #2563eb;
  background: #f0f9ff;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.code {
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.name {
  font-weight: 600;
  font-size: 14px;
  color: #111827;
  margin-top: 6px;
  line-height: 1.4;
}

.price {
  margin-top: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.3px;
}

.change {
  margin-top: 6px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.4;
}

.change.up {
  color: #ef4444;
}

.change.down {
  color: #2563eb;
}

@media (max-width: 640px) {
  .ticker-row {
    gap: 10px;
  }

  .ticker-card {
    min-width: 140px;
    padding: 12px;
  }

  .name {
    font-size: 13px;
  }

  .price {
    font-size: 14px;
  }

  .change {
    font-size: 11px;
  }
}
</style>
