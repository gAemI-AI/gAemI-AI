// src/stores/favoritesStore.js
import { defineStore } from "pinia";

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    // ✔ 항상 종목 "코드"만 저장하는 방식!
    favorites: [],
  }),

  actions: {
    // ⭐ 관심종목 토글 (코드 기반)
    toggleFavorite(code) {
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

