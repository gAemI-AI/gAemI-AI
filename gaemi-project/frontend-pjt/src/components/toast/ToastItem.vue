<template>
  <div class="toast-item" :class="toast.type">
    <div class="message">
      {{ toast.message }}
    </div>

    <button class="close-btn" @click="$emit('close')">
      ✕
    </button>
  </div>
</template>

<script setup>
/**
 * 🔔 Toast Item
 * - 토스트 1개의 UI
 * - 닫기 버튼 클릭 시 close 이벤트 emit
 */
defineProps({
  toast: {
    type: Object,
    required: true,
  },
});

defineEmits(["close"]);
</script>

<style scoped>
.toast-item {
  min-width: 260px;
  max-width: 360px;

  padding: 12px 14px;
  border-radius: 12px;

  background: #ffffff;
  border: 1px solid #e5e7eb;

  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;

  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  font-size: 13px;
}

/* 메시지 */
.message {
  color: #111827;
  line-height: 1.4;
  word-break: break-word;
}

/* 닫기 버튼 */
.close-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #9ca3af;
}
.close-btn:hover {
  color: #374151;
}

/* 타입별 스타일 (선택) */
.toast-item.info {
  border-left: 4px solid #2563eb;
}
.toast-item.success {
  border-left: 4px solid #16a34a;
}
.toast-item.error {
  border-left: 4px solid #dc2626;
}
</style>
