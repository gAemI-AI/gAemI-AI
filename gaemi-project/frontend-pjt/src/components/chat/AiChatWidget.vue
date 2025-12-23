<template>
  <div class="chat-widget">
    <div ref="bodyRef" class="chat-body">
      <div
        v-for="m in chatbotStore.messages"
        :key="m.id"
        class="bubble-wrapper"
        :class="m.role"
      >
        <div class="bubble">
          {{ m.content }}
        </div>

        <div v-if="m.role === 'assistant' && m.references && m.references.length > 0" class="references">
          <span class="ref-title">📚 참고 출처</span>
          <ul>
            <li v-for="(ref, idx) in m.references" :key="idx">
              {{ ref }}
            </li>
          </ul>
        </div>
      </div>

      <div v-if="chatbotStore.isLoading" class="bubble-wrapper assistant">
        <div class="bubble loading">
          <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        </div>
      </div>
    </div>

    <form class="chat-input" @submit.prevent="handleSend">
      <input
        v-model="input"
        type="text"
        :placeholder="chatbotStore.isLoading ? '답변 생성 중...' : '궁금한 내용을 입력하세요'"
        :disabled="chatbotStore.isLoading"
        autocomplete="off"
      />
      <button type="submit" :disabled="chatbotStore.isLoading || !input.trim()">
        전송
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from "vue";
import { useChatbotStore } from "@/stores/chatbotStore";

const chatbotStore = useChatbotStore();
const input = ref("");
const bodyRef = ref(null);

async function scrollToBottom() {
  await nextTick();
  if (bodyRef.value) {
    bodyRef.value.scrollTop = bodyRef.value.scrollHeight;
  }
}

async function handleSend() {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await chatbotStore.send(text);
}

watch(
  () => [chatbotStore.messages.length, chatbotStore.isLoading],
  () => scrollToBottom()
);

onMounted(() => scrollToBottom());
</script>

<style scoped>
.chat-widget {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
}

.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 메시지 래퍼 (말풍선 + 출처를 감싸는 박스) */
.bubble-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 85%;
}

.bubble-wrapper.assistant { align-self: flex-start; }
.bubble-wrapper.user { align-self: flex-end; align-items: flex-end; }
.bubble-wrapper.system { align-self: center; align-items: center; max-width: 90%; }

/* 말풍선 공통 */
.bubble {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.bubble-wrapper.assistant .bubble {
  background: white;
  color: #333;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.bubble-wrapper.user .bubble {
  background: #3182f6;
  color: white;
  border-bottom-right-radius: 4px;
}

.bubble-wrapper.system .bubble {
  background: rgba(0,0,0,0.05);
  color: #666;
  font-size: 12px;
  border: none;
  box-shadow: none;
  text-align: center;
}

/* ✅ 참고문헌 스타일 */
.references {
  margin-left: 4px; /* 말풍선 라인에 맞춤 */
  background: #f1f3f5;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #4e5968;
}

.ref-title {
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
  color: #333;
}

.references ul {
  margin: 0;
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.references li {
  line-height: 1.4;
}

/* 로딩 애니메이션 */
.bubble.loading {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  width: fit-content;
}
.dot {
  animation: bounce 1.4s infinite ease-in-out both;
  font-weight: bold;
  color: #8b95a1;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 입력창 */
.chat-input {
  padding: 12px;
  border-top: 1px solid #f2f4f6;
  background: white;
  display: flex;
  gap: 8px;
}
.chat-input input {
  flex: 1;
  border-radius: 20px;
  border: 1px solid #e5e8eb;
  background: #f9fafb;
  padding: 10px 16px;
  font-size: 14px;
  outline: none;
}
.chat-input input:focus {
  background: white;
  border-color: #3182f6;
}
.chat-input button {
  border-radius: 20px;
  border: none;
  background: #3182f6;
  color: white;
  padding: 0 20px;
  font-weight: 600;
  cursor: pointer;
}
.chat-input button:disabled {
  background: #e5e8eb;
  color: #b0b8c1;
}
</style>