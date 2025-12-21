<template>
  <div class="chatbot-page">
    <!-- 헤더 -->
    <header class="page-header">
      <h1>AI 챗봇</h1>
      <p class="desc">RAG 기반 주식·뉴스 분석</p>
    </header>

    <!-- 채팅 영역 -->
    <section class="chat-area">
      <AiChatWidget />
    </section>
  </div>
</template>

<script setup>
import AiChatWidget from "@/components/chat/AiChatWidget.vue";
</script>

<style scoped>
.chatbot-page {
  height: calc(100vh - 88px); /* 상단 헤더 높이 제외 */
  display: flex;
  flex-direction: column;
}

/* 페이지 상단 */
.page-header {
  padding: 12px 0 16px;
}

.page-header h1 {
  font-size: 20px;
  font-weight: 700;
}

.page-header .desc {
  font-size: 13px;
  color: #6b7280;
}

/* 🔥 채팅 영역이 화면을 채우게 만드는 핵심 */
.chat-area {
  flex: 1;                 /* 남은 높이 전부 차지 */
  display: flex;
  flex-direction: column;
  min-height: 0;           /* overflow 필수 */
}
</style>
