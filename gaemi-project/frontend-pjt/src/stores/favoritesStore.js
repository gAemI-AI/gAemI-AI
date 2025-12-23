// src/stores/favoritesStore.js
import { defineStore } from "pinia";
import api from "@/api/axios";

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    favorites: [],
    isLoaded: false,
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
      this.favorites = saved ? JSON.parse(saved) : [];
      this.isLoaded = true;
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
        await this.addFavorite(stockCode);
      }
    },

    async addFavorite(stockCode) {
      try {
        if (this.favorites.some(f => f.stock === stockCode)) return;

        await api.post("/watchlist/", {
          stock: stockCode, // ⭐ 핵심
        });

        await this.fetchWatchlist();
      } catch (err) {
        console.error("관심종목 추가 실패", err);
      }
    },

    async removeFavorite(stockCode) {
      try {
        await api.delete(`/watchlist/${stockCode}/`);
        await this.fetchWatchlist();
      } catch (err) {
        console.error("관심종목 삭제 실패", err);
      }
    },
  },
});
