// src/stores/favoritesStore.js
import { defineStore } from "pinia";

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    // ✔ 항상 종목 "코드"만 저장하는 방식!
    favorites: [],
  }),

  actions: {
    // ✅ API에서 관심종목 조회
    async fetchWatchlist() {
      const accessToken = localStorage.getItem("accessToken");
      if (!accessToken) return;

      try {
        const response = await fetch("http://localhost:8000/api/v1/watchlist/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${accessToken}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          // stock 필드에서 종목 코드 추출
          this.favorites = data.map(item => item.stock);
          this.saveToLocal();
        }
      } catch (error) {
        console.warn("관심종목 API 로드 실패:", error);
      }
    },

    loadFromLocal() {
      const saved = localStorage.getItem("favorites");
      if (saved) {
        this.favorites = JSON.parse(saved);
      }
    },

    // ⭐ 관심종목 추가
    addFavorite(code) {
      if (!this.favorites.includes(code)) {
        this.favorites.push(code);
        this.saveToLocal();
      }
    },

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

