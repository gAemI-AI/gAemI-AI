<template>
  <div class="toast-container">
    <TransitionGroup name="toast-transition">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="toast-item"
        :class="`toast-${toast.type}`"
      >
        <div class="toast-icon">
          <span v-if="toast.type === 'success'" class="icon">✓</span>
          <span v-else-if="toast.type === 'error'" class="icon">⚠</span>
          <span v-else class="icon">ℹ</span>
        </div>

        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>

        <button class="toast-close" @click="toastStore.remove(toast.id)">
          ×
        </button>

        <!-- 프로그레스 바 -->
        <div
          v-if="toast.duration"
          class="toast-progress"
          :style="{ animationDuration: `${toast.duration}ms` }"
          @animationend="toastStore.remove(toast.id)"
        ></div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToastStore } from "@/stores/toastStore";

const toastStore = useToastStore();
</script>

<style scoped>
/* 컨테이너 */
.toast-container {
  position: fixed;
  bottom: 120px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 99999;
  pointer-events: none;
}

/* 토스트 아이템 */
.toast-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 320px;
  max-width: 400px;
  padding: 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  pointer-events: all;
  position: relative;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(400px) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0) translateY(0);
  }
}

/* 성공 토스트 */
.toast-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-left: 4px solid #06b6d4;
}

/* 에러 토스트 */
.toast-error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-left: 4px solid #f87171;
}

/* 정보 토스트 */
.toast-info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-left: 4px solid #60a5fa;
}

/* 아이콘 */
.toast-icon {
  flex-shrink: 0;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.toast-success .icon {
  color: #fff;
}

.toast-error .icon {
  color: #fff;
}

.toast-info .icon {
  color: #fff;
}

/* 콘텐츠 */
.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 13px;
  opacity: 0.95;
  line-height: 1.4;
}

/* 닫기 버튼 */
.toast-close {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: inherit;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  opacity: 0.7;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  opacity: 1;
}

/* 프로그레스 바 */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.4);
  animation: progress linear forwards;
}

@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* 트랜지션 */
.toast-transition-enter-active,
.toast-transition-leave-active {
  transition: all 0.3s ease;
}

.toast-transition-enter-from {
  opacity: 0;
  transform: translateX(400px);
}

.toast-transition-leave-to {
  opacity: 0;
  transform: translateX(400px);
}
</style>
