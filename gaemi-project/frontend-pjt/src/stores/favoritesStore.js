// src/stores/favoritesStore.js
import { getWatchlist, addWatchlist, removeWatchlist } from "@/api/watchlist";
import { defineStore } from "pinia";

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    // ✔ 항상 종목 "코드"만 저장하는 방식!
    favorites: [],
  }),

  actions: {
    loadFromLocal() {
      const saved = localStorage.getItem("favorites");
      if (saved) {
        this.favorites = JSON.parse(saved);
      }
    },

    // 서버에서 관심종목 로드
    async fetchWatchlist() {
      try {
        const data = await getWatchlist();
        // ⚠️ 백엔드 응답 구조에 맞게 조정 필요
        // 예: [{ stock_id, stock_code }, ...]
        this.favorites = data.map(item => item.stock_code);
      } catch (e) {
        console.error("watchlist fetch error", e);
      }
    },

    // ⭐ 관심종목 토글 (코드 기반)
    async toggleFavorite(stock) {
      if (this.favorites.includes(code)) {
        this.favorites = this.favorites.filter((c) => c !== code);
      } else {
        this.favorites.push(code);
      }
      this.saveToLocal();
    },

    // ⭐ 관심종목 삭제
    removeFavorite(code) {
      this.favorites = this.favorites.filter((c) => c !== code);
      this.saveToLocal();
    },

    // ⭐ 로그인 시 로드
    loadFavorites(list) {
      this.favorites = [...list];
    },

    // ⭐ 로컬 저장
    saveToLocal() {
      localStorage.setItem("favorites", JSON.stringify(this.favorites));
    },
  },
});

