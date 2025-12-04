// src/stores/alertsStore.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useAlertsStore = defineStore("alerts", () => {
  const alerts = ref([]);

  function addAlert(alert) {
    alerts.value.push({
      id: Date.now(),
      enabled: true,
      ...alert
    });
  }

  function removeAlert(id) {
    alerts.value = alerts.value.filter(a => a.id !== id);
  }

  function toggleAlert(item) {
    item.enabled = !item.enabled;
  }

  return { alerts, addAlert, removeAlert, toggleAlert };
});
