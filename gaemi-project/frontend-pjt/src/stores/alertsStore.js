import { defineStore } from "pinia";
import api from "@/api/axios"; // ✅ Axios 인스턴스 import

export const useAlertsStore = defineStore("alerts", {
  state: () => ({
    alerts: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    // 특정 종목에 걸린 알림이 있는지 확인 (관심종목 삭제 시 경고용)
    hasAlertsForStock: (state) => (stockCode) => {
      return state.alerts.some((a) => a.stockCode === stockCode);
    },
  },

  actions: {
    /* --------------------------------------------------
       ✅ [핵심 1] 로그아웃 시 데이터 초기화 (auth.js에서 호출)
    -------------------------------------------------- */
    clearAlerts() {
      this.alerts = [];
      this.error = null;
    },

    /* --------------------------------------------------
       ✅ [핵심 2] 내 알림 목록 가져오기 (API)
    -------------------------------------------------- */
    async fetchAlerts() {
      this.isLoading = true;
      this.error = null;
      try {
        // GET /alerts/ -> 유저 토큰에 맞는 알림 목록 반환 가정
        const res = await api.get("/alerts/");
        this.alerts = res.data;
      } catch (e) {
        console.error("알림 목록 로드 실패:", e);
        this.error = "알림을 불러오지 못했습니다.";
        // 에러 시 빈 배열 유지
        this.alerts = [];
      } finally {
        this.isLoading = false;
      }
    },

    /* --------------------------------------------------
       알림 추가 (API)
    -------------------------------------------------- */
    async addAlert(payload) {
      // payload: { stockCode, stockName, condition, target }
      // 프론트에서 먼저 보여주기 (Optimistic Update)
      const tempId = Date.now();
      const newAlert = { ...payload, id: tempId, enabled: true };
      this.alerts.push(newAlert);

      try {
        // POST /alerts/
        const res = await api.post("/alerts/", {
          stock_code: payload.stockCode, // 백엔드 필드명에 맞게 조정 필요 (snake_case 가정)
          stock_name: payload.stockName,
          condition: payload.condition,
          target_price: payload.target,
        });
        
        // 성공 시 실제 ID로 교체 (또는 목록 다시 불러오기)
        const index = this.alerts.findIndex(a => a.id === tempId);
        if (index !== -1) {
          this.alerts[index] = res.data; // 서버가 준 데이터(id 포함)로 교체
        }
      } catch (e) {
        console.error("알림 추가 실패:", e);
        // 실패 시 롤백
        this.alerts = this.alerts.filter(a => a.id !== tempId);
        alert("알림 추가에 실패했습니다.");
      }
    },

    /* --------------------------------------------------
       알림 삭제 (API)
    -------------------------------------------------- */
    async removeAlert(id) {
      // 프론트에서 먼저 제거
      const backup = [...this.alerts];
      this.alerts = this.alerts.filter((a) => a.id !== id);

      try {
        await api.delete(`/alerts/${id}/`);
      } catch (e) {
        console.error("알림 삭제 실패:", e);
        this.alerts = backup; // 실패 시 복구
        alert("알림 삭제에 실패했습니다.");
      }
    },

    /* --------------------------------------------------
       종목 코드로 알림 일괄 삭제 (관심종목 해제 시)
    -------------------------------------------------- */
    async removeByStockCode(stockCode) {
      // 해당 종목의 알림 ID들 찾기
      const targets = this.alerts.filter(a => a.stockCode === stockCode);
      
      // 프론트 삭제
      this.alerts = this.alerts.filter(a => a.stockCode !== stockCode);

      // 백엔드 삭제 요청 (일괄 삭제 API가 없으면 반복문으로 처리)
      try {
        // 방법 1: 일괄 삭제 API가 있다면
        // await api.delete(`/alerts/stock/${stockCode}/`);
        
        // 방법 2: 개별 삭제 반복 (임시)
        await Promise.all(targets.map(t => api.delete(`/alerts/${t.id}/`)));
      } catch (e) {
        console.error("종목 관련 알림 삭제 실패:", e);
        // 복구 로직은 복잡하므로 생략하거나, 다시 fetch
        this.fetchAlerts();
      }
    },

    /* --------------------------------------------------
       알림 ON/OFF 토글 (API)
    -------------------------------------------------- */
    async toggleAlert(id) {
      const alert = this.alerts.find((a) => a.id === id);
      if (!alert) return;

      const oldValue = alert.enabled;
      // 프론트 반영
      // (AlertList.vue의 v-model로 이미 값이 변했을 수 있으므로 여기선 API 호출만 집중)
      
      try {
        await api.patch(`/alerts/${id}/`, { enabled: alert.enabled });
      } catch (e) {
        console.error("알림 토글 실패:", e);
        alert.enabled = oldValue; // 실패 시 원상복구
      }
    },
  },
});