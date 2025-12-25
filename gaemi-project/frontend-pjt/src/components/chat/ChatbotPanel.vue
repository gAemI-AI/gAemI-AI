<template>
  <transition name="slide-up">
    <div class="chatbot-panel">
      <header class="panel-header">
        <div class="header-left">
          <div class="brand-icon">
            <img src="@/assets/logo/gaemi.png" alt="logo" />
          </div>
          <div class="header-text">
            <h2 class="title">gAemI 챗봇</h2>
            <span class="status">● 실시간 답변 중</span>
          </div>
        </div>
        <button class="close-btn" @click="closeChat">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6L18 18" stroke="#6b7684" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </header>

      <div class="panel-body">
        <AiChatWidget />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useChatbotStore } from "@/stores/chatbotStore";
import AiChatWidget from "@/components/chat/AiChatWidget.vue";

const chatbotStore = useChatbotStore();

const closeChat = () => {
  chatbotStore.close();
};
</script>

<style scoped>
.chatbot-panel {
  position: fixed;
  right: 24px;
  bottom: 24px; /* FAB 위치와 동일 */

  width: 400px; /* 조금 더 넓게 */
  height: 600px; /* 조금 더 길게 */
  max-height: calc(100vh - 48px); /* 화면 넘어가지 않게 */
  
  border-radius: 24px; /* 둥근 모서리 */
  background: #ffffff;
  
  /* 깊이감 있는 그림자 */
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.12), 
              0 4px 16px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0,0,0,0.05);

  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 100; /* FAB보다 높게 */
}

/* 헤더 */
.panel-header {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px); /* 블러 효과 */
  border-bottom: 1px solid #f2f4f6;

  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon img {
  width: 32px;
  height: 32px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 16px;
  font-weight: 700;
  color: #191f28;
  margin: 0;
  line-height: 1.2;
}

.status {
  font-size: 11px;
  color: #3182f6; /* 토스 블루 */
  font-weight: 600;
  margin-top: 2px;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f2f4f6;
}

/* 본문 영역 */
.panel-body {
  flex: 1;
  background: #f9fafb; /* 대화창 배경은 아주 연한 회색 */
  overflow: hidden; /* 스크롤은 AiChatWidget 내부에서 처리 */
  display: flex;
  flex-direction: column;
}

/* 슬라이드 애니메이션 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>