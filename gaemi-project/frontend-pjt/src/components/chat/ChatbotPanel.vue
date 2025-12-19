<template>
  <div class="chatbot-panel">
    <!-- 헤더 -->
    <header class="panel-header">
      <div class="header-text">
        <div class="title">AI 챗봇</div>
        <div class="subtitle">RAG 기반 분석</div>
      </div>
      <button class="close-btn" @click="closeChat">✕</button>
    </header>

    <!-- 본문: 기존 AI 챗봇 UI -->
    <div class="panel-body">
      <AiChatWidget />
    </div>
  </div>
</template>

<script setup>
import { useChatbotStore } from "@/stores/chatbotStore";
import AiChatWidget from "@/components/chat/AiChatWidget.vue";

/**
 * 🤖 Chatbot Panel
 * - 전역 챗봇 패널 컨테이너
 * - 열림/닫힘은 store에서 제어
 * - 내부 UI는 AiChatWidget에 위임
 */
const chatbotStore = useChatbotStore();

const closeChat = () => {
  chatbotStore.close();
};
</script>

<style scoped>
.chatbot-panel {
  position: fixed;
  right: 24px;
  bottom: 24px;

  width: 380px;
  height: 460px;
  border-radius: 16px;

  background: #ffffff;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.3);

  display: flex;
  flex-direction: column;

  z-index: 45;
}

/* 헤더 */
.panel-header {
  padding: 10px 14px;
  border-bottom: 1px solid #e5e7eb;

  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text .title {
  font-weight: 600;
}
.header-text .subtitle {
  font-size: 12px;
  color: #6b7280;
}

.close-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
}

/* 본문 */
.panel-body {
  flex: 1;
  overflow: hidden;
}
</style>
