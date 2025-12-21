<template>
  <div class="toast-stack">
    <div
      v-for="toast in toastStore.toasts"
      :key="toast.id"
      class="toast"
      :class="toast.type"
    >
      <div class="title">{{ toast.title }}</div>
      <div class="message">{{ toast.message }}</div>

      <button class="close" @click="toastStore.remove(toast.id)">✕</button>
    </div>
  </div>
</template>

<script setup>
import { useToastStore } from "@/stores/toastStore";

const toastStore = useToastStore();
</script>

<style scoped>
.toast-stack {
  position: fixed;
  right: 24px;
  bottom: 100px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 60;
}

.toast {
  background: white;
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  width: 260px;
  position: relative;
}

.toast.info {
  border-left: 4px solid #2563eb;
}

.toast.warning {
  border-left: 4px solid #f59e0b;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.title {
  font-weight: 600;
  font-size: 13px;
}

.message {
  font-size: 12px;
  color: #4b5563;
  margin-top: 4px;
}

.close {
  position: absolute;
  top: 6px;
  right: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
}
</style>
