<!-- src/components/common/FavoriteButton.vue -->
<template>
  <button class="star-btn" @click="toggle">
    <span :class="{ active: isFavorite }">★</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useFavoritesStore } from '@/stores/favoritesStore.js'

const props = defineProps({
  stock: { type: Object, required: true }
})

const store = useFavoritesStore()

const isFavorite = computed(() =>
  store.favorites.some((f) => f.code === props.stock.code)
)

function toggle() {
  store.toggleFavorite(props.stock)
}
</script>

<style scoped>
.star-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 24px;
  padding: 4px;
}
.star-btn span {
  color: #d1d5db;
}
.star-btn span.active {
  color: #2563eb;
}
</style>
