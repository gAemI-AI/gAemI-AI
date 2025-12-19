// src/stores/alertEventsStore.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useToastStore } from "@/stores/toastStore";

export const useAlertEventsStore = defineStore("alertEvents", () => {
  /* ------------------------
     State
  ------------------------ */
  const events = ref([]);

  /* ------------------------
     Getters
  ------------------------ */
  const latestEvents = computed(() =>
    [...events.value].sort(
      (a, b) => new Date(b.triggeredAt) - new Date(a.triggeredAt)
    )
  );

  const count = computed(() => events.value.length);

  /* ------------------------
     LocalStorage (선택)
  ------------------------ */
  function saveToLocal() {
    localStorage.setItem("alert_events", JSON.stringify(events.value));
  }

  function loadFromLocal() {
    const saved = localStorage.getItem("alert_events");
    if (!saved) return;

    try {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) events.value = parsed;
    } catch (e) {
      // 파싱 실패 시 무시
    }
  }

  // ⭐ 새로고침 유지
  loadFromLocal();

  /* ------------------------
     Actions
  ------------------------ */
  function addEvent(event) {
    /*
      event 구조 예시 (Flink / WebSocket 기준)
      {
        stockCode,
        stockName,
        condition,
        target,
        currentPrice,
        triggeredAt
      }
    */

    const alertEvent = {
      id: Date.now(),
      stockCode: event.stockCode,
      stockName: event.stockName,
      condition: event.condition,
      target: event.target,
      currentPrice: event.currentPrice,
      triggeredAt: event.triggeredAt || new Date().toISOString(),
    };

    // 1️⃣ 이벤트 저장
    events.value.push(alertEvent);
    saveToLocal();

    // 2️⃣ 토스트 발생 (🔥 여기서만)
    const toastStore = useToastStore();
    toastStore.push({
      type: "info",
      title: "알림 도착",
      message: `${alertEvent.stockName} ${alertEvent.target}원 조건 충족`,
    });
  }

  function clearEvents() {
    events.value = [];
    saveToLocal();
  }

  return {
    // state
    events,

    // getters
    latestEvents,
    count,

    // actions
    addEvent,
    clearEvents,
  };
});
