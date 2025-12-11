<!-- src/components/common/FavoriteButton.vue -->
<template>
  <button class="star-btn" @click="toggleFavorite">
    <span :class="{ active: isFavorite }">★</span>
  </button>
</template>

<script setup>
import { computed } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";

const props = defineProps({
  stock: { type: Object, required: true },
});

const store = useFavoritesStore();

// ✔ store는 코드 기반으로 저장하므로 코드 비교만 하면 됨!
const isFavorite = computed(() =>
  store.favorites.includes(props.stock.code)
);

function toggleFavorite() {
  store.toggleFavorite(props.stock.code);
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
