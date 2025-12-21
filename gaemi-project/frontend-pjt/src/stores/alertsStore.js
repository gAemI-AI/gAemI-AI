// src/stores/alertsStore.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";

const CONDITION_META = {
  gte: { label: "가격 이상", unit: "원" },
  lte: { label: "가격 이하", unit: "원" },
  changeUp: { label: "전일 대비 상승률 이상", unit: "%" },
  changeDown: { label: "전일 대비 하락률 이하", unit: "%" },
};

function makeDescription(condition, target) {
  const meta = CONDITION_META[condition];
  if (!meta) return "";
  return `${meta.label}: ${target}${meta.unit}`;
}

export const useAlertsStore = defineStore("alerts", () => {
  // ✅ 알림 "조건" 원본
  const alerts = ref([]);

  /* ------------------------
     LocalStorage
  ------------------------ */
  function saveToLocal() {
    localStorage.setItem("alerts", JSON.stringify(alerts.value));
  }

  function loadFromLocal() {
    const saved = localStorage.getItem("alerts");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) alerts.value = parsed;
      } catch (e) {
        // 파싱 실패 시 무시
      }
    }
  }

  // ✅ 초기 로드 시 LocalStorage에서 데이터 불러오기
  loadFromLocal();

  /* ------------------------
     대시보드용 "알림 내역" 형태로 변환
  ------------------------ */
  const alertEvents = computed(() =>
    alerts.value
      .filter((a) => a.enabled !== false) // enabled true만 노출
      .slice() // 원본 보호
      .reverse() // 최신이 위로
      .map((a) => ({
        id: a.id,
        stockName: a.stockName,
        title: a.description || makeDescription(a.condition, a.target),
        time: "설정됨",
        statusClass: "working",
        stockCode: a.stockCode,
        condition: a.condition,
        target: a.target,
      }))
  );

  /* ------------------------
     CRUD
  ------------------------ */
  function addAlert({ stockCode, stockName, condition, target }) {
    alerts.value.push({
      id: Date.now(),
      stockCode,
      stockName,
      condition,
      target,
      description: makeDescription(condition, target),
      enabled: true,
    });
    saveToLocal(); // 새로 추가된 알림은 로컬스토리지에 즉시 저장
  }

  function removeAlert(id) {
    alerts.value = alerts.value.filter((a) => a.id !== id);
    saveToLocal(); // 알림 삭제 후 로컬스토리지 업데이트
  }

  function toggleAlert(id) {
    const alert = alerts.value.find((a) => a.id === id);
    if (!alert) return;
    alert.enabled = !alert.enabled;
    saveToLocal(); // 알림 상태 변경 후 로컬스토리지 업데이트
  }

  /* ------------------------
     관심 종목 연동
  ------------------------ */
  function hasAlertsForStock(stockCode) {
    return alerts.value.some((a) => a.stockCode === stockCode);
  }

  function removeByStockCode(stockCode) {
    alerts.value = alerts.value.filter((a) => a.stockCode !== stockCode);
    saveToLocal(); // 관심 종목 삭제 후 로컬스토리지 업데이트
  }

  return {
    alerts,
    alertEvents, // 대시보드에서 쓰는 값

    addAlert,
    removeAlert,
    toggleAlert,
    hasAlertsForStock,
    removeByStockCode,

    loadFromLocal,
    saveToLocal,
  };
});
