// src/stores/alertsStore.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { fetchNotificationRules, createNotificationRule, deleteNotificationRule } from "@/api/notifications";

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
  const isLoaded = ref(false);
  const lastError = ref(null);

  /* ------------------------
     대시보드용 "알림 내역" 형태로 변환
  ------------------------ */
  const alertEvents = computed(() =>
    alerts.value
      .slice() // 원본 보호
      .reverse() // 최신이 위로
      .map((a) => ({
        id: a.id ?? a.rule_id ?? a.notification_id,
        stockName: a.stockName || a.stockCode,
        title: a.description || makeDescription(a.condition, a.target),
        time: "설정됨",
        statusClass: "working",
        stockCode: a.stockCode,
        condition: a.condition,
        target: a.target,
      }))
  );

  // id 통일 헬퍼 (위쪽에 추가)
  function pickId(obj) {
    return obj?.id ?? obj?.rule_id ?? obj?.notification_id ?? null;
  }

  async function fetchAlerts() {
    lastError.value = null;

    try {
      const data = await fetchNotificationRules();

      alerts.value = (Array.isArray(data) ? data : [])
        .map((r) => {
          const condition = r.condition ?? r.operator;
          const target = r.target_price ?? r.target_value ?? r.target;

          return {
            id: pickId(r),                 // ✅ 여기 핵심
            stockCode: r.stock,
            stockName: r.stock_detail?.stock_name ?? null,
            condition,
            target,
            description: makeDescription(condition, target),
          };
        })
        .filter((a) => a.id != null);      // ✅ id 없는 찌꺼기 제거

      isLoaded.value = true;
    } catch (e) {
      console.error("알림 규칙 조회 실패", e);
      lastError.value = "알림 규칙을 불러오지 못했습니다";
      alerts.value = [];
      isLoaded.value = true;
    }
  }

  async function addAlert({ stockCode, condition, target }) {
    lastError.value = null;

    try {
      const created = await createNotificationRule({
        stock: stockCode,
        metric_type: "price",
        operator: condition,
        target_value: Number(target),
      });

      const conditionFinal = created.condition ?? created.operator ?? condition;
      const targetFinal =
        created.target ?? created.target_price ?? created.target_value ?? target;

      const newRule = {
        id: pickId(created),              // ✅ 여기 핵심
        stockCode: created.stock ?? stockCode,
        stockName: created.stock_detail?.stock_name ?? null,
        condition: conditionFinal,
        target: targetFinal,
        description: makeDescription(conditionFinal, targetFinal),
      };

      if (newRule.id == null) {
        // 생성 응답에 id가 없으면, fetch로 동기화하는 게 안전
        await fetchAlerts();
        return;
      }

      alerts.value.push(newRule);
    } catch (e) {
      console.error("알림 규칙 생성 실패", e);
      lastError.value = "알림 규칙 생성에 실패했습니다.";
      throw e;
    }
  }

  async function removeAlert(ruleId) {
    lastError.value = null;

    // ✅ 방어코드 (undefined 들어오는 순간 바로 잡기)
    if (ruleId == null) {
      console.error("removeAlert called with invalid ruleId:", ruleId);
      lastError.value = "삭제할 알림 id가 없습니다. 새로고침 후 다시 시도하세요.";
      return;
    }

    try {
      await deleteNotificationRule(ruleId);
      alerts.value = alerts.value.filter((a) => a.id !== ruleId);
    } catch (e) {
      console.error("알림 규칙 삭제 실패", e);
      lastError.value = "알림 규칙 삭제에 실패했습니다.";
      throw e;
    }
  }


  // function toggleAlert(id) {
  //   const alert = alerts.value.find((a) => a.id === id);
  //   if (!alert) return;
  //   alert.enabled = !alert.enabled;
  // }

  /* ------------------------
     관심 종목 연동
  ------------------------ */
  function hasAlertsForStock(stockCode) {
    return alerts.value.some((a) => a.stockCode === stockCode);
  }

  async function removeByStockCode(stockCode) {
    const targets = alerts.value.filter(a => a.stockCode === stockCode);

    for (const alert of targets) {
      if (!alert.id) continue; // 안전장치
      try {
        await deleteNotificationRule(alert.id);
      } catch (e) {
        console.error("알림 삭제 실패", alert.id, e);
      }
    }

    // 서버 삭제 성공 후 프론트 상태 정리
    alerts.value = alerts.value.filter(a => a.stockCode !== stockCode);
  }

  return {
    alerts,
    alertEvents, // 대시보드에서 쓰는 값

    isLoaded,
    lastError,

    fetchAlerts,
    addAlert,
    removeAlert,

    hasAlertsForStock,
    removeByStockCode,
  };
});
