<template>
  <transition name="pop">
    <button 
      v-if="!chatbotStore.isOpen" 
      class="chatbot-fab" 
      @click="openChat"
      aria-label="AI 챗봇 열기"
    >
      <div class="icon-wrapper">
        <img src="@/assets/logo/gaemi.png" alt="Chatbot" class="fab-icon" />
      </div>
      <span class="tooltip">AI 투자 비서</span>
    </button>
  </transition>
</template>

<script setup>
import { useChatbotStore } from "@/stores/chatbotStore";

const chatbotStore = useChatbotStore();

const openChat = () => {
  chatbotStore.open();
};
</script>

<style scoped>
.chatbot-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;

  width: 60px;
  height: 60px;
  border-radius: 30px; /* 완전 원형 */
  border: none;

  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 
              0 2px 8px rgba(0, 0, 0, 0.04); /* 부드러운 이중 그림자 */
  
  cursor: pointer;
  z-index: 40;

  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); /* 쫀득한 애니메이션 */
}

.chatbot-fab:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
}

.chatbot-fab:active {
  transform: scale(0.95);
}

.icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fab-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 툴팁 (마우스 오버 시 나오는 말풍선 느낌) */
.tooltip {
  position: absolute;
  right: 70px;
  background: #191f28;
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.2s ease;
  pointer-events: none;
  white-space: nowrap;
}

.chatbot-fab:hover .tooltip {
  opacity: 1;
  transform: translateX(0);
}

/* 팝업 애니메이션 */
.pop-enter-active,
.pop-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
}
</style>