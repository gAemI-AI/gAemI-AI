<template>
  <div>
    <!-- 플로팅 버튼 -->
    <button v-if="!open" class="floating-btn" @click="open = true">
      💬
    </button>

    <!-- 챗봇 패널 -->
    <div v-else class="chat-panel">
      <header class="chat-header">
        <div>
          <div class="title">AI 챗봇</div>
          <div class="subtitle">RAG 기반 분석</div>
        </div>
        <button class="close-btn" @click="open = false">✕</button>
      </header>

      <div class="chat-body">
        <div class="bubble bot">
          안녕하세요! <strong>"gAemI"</strong> AI 어시스턴트입니다. <br />
          실시간 주가 데이터와 AI 뉴스 분석을 결합한 RAG 시스템으로 응답합니다.
        </div>
        <div
          v-for="(m, idx) in messages"
          :key="idx"
          class="bubble"
          :class="m.role"
        >
          {{ m.content }}
        </div>
      </div>

      <form class="chat-input" @submit.prevent="send">
        <input
          v-model="input"
          type="text"
          placeholder="예: 삼성전자 3분기 실적 어때?"
        />
        <button type="submit">전송</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const open = ref(false);
const input = ref('');
const messages = ref([]);

function send() {
  if (!input.value.trim()) return;
  messages.value.push({ role: 'user', content: input.value });
  // 실제로는 백엔드 RAG API 호출
  messages.value.push({
    role: 'bot',
    content: '여기에 백엔드에서 받은 RAG 응답 내용을 표시합니다.',
  });
  input.value = '';
}
</script>

<style scoped>
.floating-btn {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 52px;
  height: 52px;
  border-radius: 999px;
  border: none;
  background: #2563eb;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  z-index: 50;
}

/* 패널이 떠 있어도 overlay를 깔지 않으므로,
   패널 밖 영역은 그대로 클릭/스크롤 가능 */
.chat-panel {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 380px;
  height: 460px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 50;
}

.chat-header {
  padding: 10px 14px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-header .title {
  font-weight: 600;
}
.chat-header .subtitle {
  font-size: 12px;
  color: #6b7280;
}
.close-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
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
