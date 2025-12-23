// src/stores/favoritesStore.js
import { defineStore } from "pinia";
import api from "@/api/axios";

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    favorites: [],
    isLoaded: false,
  }),

  actions: {
    /* =========================
     * 로그인 상태 분기 로딩
     * ========================= */
    async fetchWatchlist() {
      try {
        const res = await api.get("/watchlist/");
        // 백엔드 응답: [{ stock_code: "005930", ... }]
        this.favorites = res.data;
        this.isLoaded = true;
      } catch (err) {
        console.error("watchlist fetch 실패", err);
        this.favorites = [];
      }
    },

    loadFromLocal() {
      const saved = localStorage.getItem("favorites");
      this.favorites = saved ? JSON.parse(saved) : [];
      this.isLoaded = true;
    },

    saveToLocal() {
      localStorage.setItem("favorites", JSON.stringify(this.favorites));
    },

    /* =========================
     * 토글 (추가 / 삭제)
     * ========================= */
    async toggleFavorite(stockCode) {
      const hasToken = !!localStorage.getItem("accessToken");

      if (!hasToken) {
        console.warn("비로그인 관심종목은 현재 미지원");
        return;
      }
      if (this.favorites.some(f => f.stock === stockCode)) {
        await this.removeFavorite(stockCode);
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
