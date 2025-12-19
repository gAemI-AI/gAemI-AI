<template>
  <div class="chat-widget">
    <!-- 메시지 영역 -->
    <div class="chat-body">
      <div
        v-for="(m, idx) in chatbotStore.messages"
        :key="idx"
        class="bubble"
        :class="m.role"
      >
        {{ m.content }}
      </div>
    </div>

    <!-- 입력 영역 -->
    <form class="chat-input" @submit.prevent="send">
      <input
        v-model="input"
        type="text"
        placeholder="예: 삼성전자 3분기 실적 어때?"
      />
      <button type="submit">전송</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useChatbotStore } from "@/stores/chatbotStore";

const chatbotStore = useChatbotStore();
const input = ref("");

function send() {
  if (!input.value.trim()) return;
  chatbotStore.sendMessageMock(input.value);
  input.value = "";
}
</script>

<style scoped>
/* 🔑 핵심 wrapper */
.chat-widget {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-body {
  padding: 12px;
  flex: 1;
  overflow-y: auto;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.bubble {
  max-width: 80%;
  padding: 8px 10px;
  border-radius: 12px;
  font-size: 13px;
}
.bubble.bot {
  background: white;
  align-self: flex-start;
}
.bubble.user {
  background: #2563eb;
  color: white;
  align-self: flex-end;
}

.chat-input {
  padding: 10px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
}
.chat-input input {
  flex: 1;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  padding: 8px 12px;
  font-size: 13px;
}
.chat-input button {
  border-radius: 999px;
  border: none;
  background: #2563eb;
  color: white;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
}
</style>
