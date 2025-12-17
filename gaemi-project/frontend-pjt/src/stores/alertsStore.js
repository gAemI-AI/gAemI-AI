// src/stores/alertsStore.js
import { defineStore } from "pinia";
import { ref } from "vue";

const CONDITION_META = {
  gte: {
    label: "가격 이상",
    unit: "원",
  },
  lte: {
    label: "가격 이하",
    unit: "원",
  },
  changeUp: {
    label: "전일 대비 상승률 이상",
    unit: "%",
  },
  changeDown: {
    label: "전일 대비 하락률 이하",
    unit: "%",
  },
};

function makeDescription(condition, target) {
  const meta = CONDITION_META[condition];
  if (!meta) return "";

  return `${meta.label}: ${target}${meta.unit}`;
}

export const useAlertsStore = defineStore("alerts", () => {
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
      alerts.value = JSON.parse(saved);
    }
  }

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
    saveToLocal();
  }

  function removeAlert(id) {
    alerts.value = alerts.value.filter(a => a.id !== id);
    saveToLocal();
  }

  function toggleAlert(id) {
    const alert = alerts.value.find(a => a.id === id);
    if (!alert) return;

    alert.enabled = !alert.enabled;
    saveToLocal();
  }

  /* ------------------------
     관심 종목 연동
  ------------------------ */
  function hasAlertsForStock(stockCode) {
    return alerts.value.some(a => a.stockCode === stockCode);
  }

  function removeByStockCode(stockCode) {
    alerts.value = alerts.value.filter(a => a.stockCode !== stockCode);
    saveToLocal();
  }

  return {
    alerts,
    addAlert,
    removeAlert,
    toggleAlert,
    hasAlertsForStock,
    removeByStockCode,
    loadFromLocal,
  };
});
