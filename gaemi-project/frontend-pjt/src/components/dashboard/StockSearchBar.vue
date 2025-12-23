<!-- src/components/dashboard/StockSearchBar.vue -->
<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <input
        type="text"
        v-model="keyword"
        @input="emitSearch"
        placeholder="종목명 또는 코드 검색"
        class="search-input"
      />
      <button 
        v-if="keyword" 
        @click="clearSearch" 
        class="clear-btn"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const keyword = ref('')
const emit = defineEmits(['search'])

function emitSearch() {
  emit('search', keyword.value)
}

function clearSearch() {
  keyword.value = ''
  emit('search', '')
}
</script>

<style scoped>
.search-bar {
  width: 100%;
  margin-bottom: 24px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 0 14px;
  height: 48px;
  transition: all 0.2s ease;
}

.search-input-wrapper:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #9ca3af;
  margin-right: 10px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: #111827;
  font-weight: 500;
  font-family: inherit;
}

.search-input::placeholder {
  color: #9ca3af;
  font-weight: 400;
}

.clear-btn {
  border: none;
  background: none;
  cursor: pointer;
  color: #9ca3af;
  font-size: 18px;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  transition: color 0.2s ease;
}

.clear-btn:hover {
  color: #6b7280;
}

@media (max-width: 640px) {
  .search-input-wrapper {
    height: 44px;
  }

  .search-input {
    font-size: 14px;
  }
}
</style>
