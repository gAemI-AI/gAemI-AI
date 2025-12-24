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
        // GET /api/v1/notifications/rules/
        const res = await api.get("/notifications/rules/");
        // 서버 응답을 프론트 형식으로 변환
        this.alerts = (res.data || []).map(rule => ({
          id: rule.rule_id,
          stockCode: rule.stock_details?.stock_id || rule.stock,
          stockName: rule.stock_details?.stock_name || '',
          condition: 'gte', // 서버 데이터로부터 역계산 (현재는 기본값)
          target: rule.target_value,
          enabled: rule.is_active,
        }));
      } catch (e) {
        console.error("알림 목록 로드 실패:", e);
        this.error = "알림을 불러오지 못했습니다.";
        this.alerts = [];
      } finally {
        this.isLoading = false;
      }
    },

    /* --------------------------------------------------
       알림 추가 (API)
    -------------------------------------------------- */
    async addAlert(payload) {
      // payload: { stockCode, stockName, condition, target, metric_type, operator, target_value }
      const tempId = Date.now();
      const newAlert = { 
        id: tempId, 
        stockCode: payload.stockCode,
        stockName: payload.stockName,
        enabled: true,
        condition: payload.condition,
        target: payload.target,
      };
      this.alerts.push(newAlert);

      try {
        // POST /api/v1/notifications/rules/
        const res = await api.post("/notifications/rules/", {
          stock: payload.stockCode,
          metric_type: payload.metric_type,
          operator: payload.operator,
          target_value: payload.target_value,
        });
        
        // 성공 시 실제 서버 응답 데이터로 교체
        const index = this.alerts.findIndex(a => a.id === tempId);
        if (index !== -1) {
          this.alerts[index] = {
            id: res.data.rule_id,
            stockCode: payload.stockCode,
            stockName: payload.stockName,
            condition: payload.condition,
            target: payload.target,
            enabled: res.data.is_active,
          };
        }
        return res.data;
      } catch (e) {
        console.error("알림 추가 실패:", e.response?.data || e.message);
        // 실패 시 롤백
        this.alerts = this.alerts.filter(a => a.id !== tempId);
        throw new Error(e.response?.data?.detail || e.response?.data?.[0] || "알림을 추가할 수 없습니다.");
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
        await api.delete(`/notifications/rules/${id}/`);
      } catch (e) {
        console.error("알림 삭제 실패:", e);
        this.alerts = backup; // 실패 시 복구
        throw new Error(e.response?.data?.detail || "알림을 삭제할 수 없습니다.");
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

      // 백엔드 삭제 요청
      try {
        await Promise.all(targets.map(t => api.delete(`/notifications/rules/${t.id}/`)));
      } catch (e) {
        console.error("종목 관련 알림 삭제 실패:", e);
        // 복구
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
      
      try {
        await api.patch(`/notifications/rules/${id}/`, { is_active: alert.enabled });
      } catch (e) {
        console.error("알림 토글 실패:", e);
        alert.enabled = oldValue; // 실패 시 원상복구
      }
    },
  },
});