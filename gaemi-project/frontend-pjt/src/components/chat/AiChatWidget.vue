<template>
  <div class="chat-widget">
    <!-- 메시지 영역 -->
    <div ref="bodyRef" class="chat-body">
      <div
        v-for="m in chatbotStore.messages"
        :key="m.id || m.createdAt || m.content"
        class="bubble"
        :class="bubbleClass(m.role)"
      >
        <!--assistant만 markdown 렌더링-->
        <div v-if="m.role === 'assistant'" v-html="renderContent(m)" />
        <div v-else>
          {{ m.content }}
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <form class="chat-input" @submit.prevent="send">
      <input
        v-model="input"
        type="text"
        placeholder="예: 삼성전자 3분기 실적 어때?"
        autocomplete="off"
      />
      <button type="submit">전송</button>
    </form>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { useChatbotStore } from "@/stores/chatbotStore";
import { marked } from "marked";

const chatbotStore = useChatbotStore();
const input = ref("");
const bodyRef = ref(null);

function renderContent(message) {
  if (message.role === 'assistant') {
    return marked.parse(message.content);
  }
  return message.content;
}

function bubbleClass(role) {
  // store role: "user" | "assistant" | "system"
  if (role === "assistant") return "bot";
  return role; // "user", "system"
}

async function send() {
  const text = input.value.trim();
  if (!text) return;

  // ✅ store에 있는 액션 사용 (너가 올린 store에는 send(text)만 있음)
  await chatbotStore.send(text);

  input.value = "";

  // ✅ 전송 후 맨 아래로 스크롤
  await nextTick();
  if (bodyRef.value) {
    bodyRef.value.scrollTop = bodyRef.value.scrollHeight;
  }
}
</script>

<style scoped>
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
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ✅ assistant -> bot */
.bubble.bot {
  background: white;
  align-self: flex-start;
  border: 1px solid #e5e7eb;
}

/* ✅ user */
.bubble.user {
  background: #2563eb;
  color: white;
  align-self: flex-end;
}

/* (선택) system 메시지 */
.bubble.system {
  background: white;
  color: #111827;
  align-self: flex-start;
  border: 1px solid #e5e7eb;
}


.chat-input {
  padding: 10px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
}

.chat-input input {
  flex: 1;
  min-width: 0;
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
