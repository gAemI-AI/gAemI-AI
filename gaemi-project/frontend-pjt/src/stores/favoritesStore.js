// src/stores/favoritesStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref([])

  function toggleFavorite(stock) {
    const idx = favorites.value.findIndex((s) => s.code === stock.code)
    if (idx === -1) favorites.value.push(stock)
    else favorites.value.splice(idx, 1)
  }

  // ⭐ 추가: 개별 종목 삭제
  function removeFavorite(code) {
    favorites.value = favorites.value.filter((item) => item.code !== code)
  }

  return { favorites, toggleFavorite, removeFavorite }
})
