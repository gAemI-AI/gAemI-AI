<template>
  <button class="chatbot-fab" @click="openChat">
    💬
  </button>
</template>

<script setup>
import { useChatbotStore } from "@/stores/chatbotStore";

/**
 * 💬 Chatbot Floating Action Button
 * - 챗봇을 여는 전역 플로팅 버튼
 * - 상태 관리는 store에 위임
 */
const chatbotStore = useChatbotStore();

const openChat = () => {
  chatbotStore.openChat();
};
</script>

<style scoped>
.chatbot-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;

  width: 52px;
  height: 52px;
  border-radius: 999px;
  border: none;

  background: #2563eb;
  color: #ffffff;
  font-size: 24px;

  cursor: pointer;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  z-index: 40;

  display: flex;
  align-items: center;
  justify-content: center;
}

.chatbot-fab:hover {
  background: #1d4ed8;
}
</style>
