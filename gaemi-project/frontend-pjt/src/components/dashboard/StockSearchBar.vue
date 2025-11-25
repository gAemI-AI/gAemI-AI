<!-- src/components/dashboard/StockSearchBar.vue -->
<template>
  <div class="search-bar">
    <input
      type="text"
      v-model="keyword"
      @input="emitSearch"
      placeholder="종목명 또는 코드 입력..."
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const keyword = ref('')
const emit = defineEmits(['search'])

function emitSearch() {
  emit('search', keyword.value)
}
</script>

<style scoped>
.search-bar {
  width: 100%;
}
.search-bar input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 14px;
}
</style>
