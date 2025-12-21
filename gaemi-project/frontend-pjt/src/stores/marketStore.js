// src/stores/marketStore.js
import { defineStore } from "pinia";

export const useMarketStore = defineStore("market", {
  state: () => ({
    // 시장 지수 요약
    kospi: {
      price: 2645.85,
      diff: 15.32,
      rate: 0.58,
    },
    kosdaq: {
      price: 745.12,
      diff: -3.45,
      rate: -0.46,
    },

    isLoading: false,
    lastUpdatedAt: null,
  }),

  getters: {
    isKospiUp: (state) => state.kospi.diff >= 0,
    isKosdaqUp: (state) => state.kosdaq.diff >= 0,
  },

  actions: {
    /* ---------------------------------
       🔹 더미 로딩 (현재 사용)
    --------------------------------- */
    loadMock() {
      this.lastUpdatedAt = new Date().toISOString();
    },

    /* ---------------------------------
       🔹 나중에 API 붙일 자리
       예: GET /api/market/summary
    --------------------------------- */
    async fetchMarketSummary() {
      this.isLoading = true;

      try {
        // TODO: 실제 API 연결
        // const res = await api.get("/market/summary");
        // this.kospi = res.data.kospi;
        // this.kosdaq = res.data.kosdaq;

        // 임시 mock (지금은 안 씀)
        await new Promise((r) => setTimeout(r, 300));
        this.lastUpdatedAt = new Date().toISOString();
      } catch (e) {
        console.error("시장 지수 조회 실패", e);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
