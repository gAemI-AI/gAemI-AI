// src/stores/marketStore.js
import { defineStore } from "pinia";
import api from "@/api/axios";

export const useMarketStore = defineStore("market", {
  state: () => ({
    kospi: null,
    kosdaq: null,

    isLoading: false,
    lastUpdatedAt: null,
  }),

  getters: {
    isKospiUp: (state) => state.kospi && state.kospi.diff >= 0,
    isKosdaqUp: (state) => state.kosdaq && state.kosdaq.diff >= 0,
  },

  actions: {
    async fetchMarketIndex() {
      this.isLoading = true;

      try {
        const res = await api.get("/stocks/market-index/");
        
        const data = res.data;
        if (!Array.isArray(data) || data.length === 0) {
          this.kospi = null;
          this.kosdaq = null;
          this.lastUpdatedAt = new Date().toISOString();
          return;
        }
        const kospi = data.find((m) => m.name === "KOSPI");
        const kosdaq = data.find((m) => m.name === "KOSDAQ");

        this.kospi = kospi ? {
          price: kospi.price,
          diff: kospi.diff,
          rate: kospi.rate,
        } : null;

        this.kosdaq = kosdaq ? {
          price: kosdaq.price,
          diff: kosdaq.diff,
          rate: kosdaq.rate,
        } : null;

        this.lastUpdatedAt = new Date().toISOString();
      } catch (e) {
        console.error("시장 지수 조회 실패", e);
      } finally {
        this.isLoading = false;
      }
    },
  },
});