<template>
  <div class="chatbot-page">
    <div class="chat-container">
      <header class="page-header">
        <div class="header-content">
          <h1 class="page-title">gAemI-AI 챗봇</h1>
          <p class="page-desc">궁금한 종목이나 시장 상황을 물어보세요</p>
        </div>
      </header>

      <section class="chat-area">
        <AiChatWidget />
      </section>
    </div>
  </div>
</template>

<script setup>
import AiChatWidget from "@/components/chat/AiChatWidget.vue";
</script>

<style scoped>
.chatbot-page {
  /* 화면 전체 높이에서 헤더 높이만큼 뺌 */
  height: calc(100vh - 60px); 
  background: #f9fafb;
  display: flex;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
}

.chat-container {
  width: 100%;
  max-width: 800px; /* 너무 넓어지지 않게 제한 */
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* 헤더 */
.page-header {
  text-align: center;
  margin-bottom: 8px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #191f28;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 15px;
  color: #8b95a1;
  margin: 0;
}

/* 채팅 영역 */
.chat-area {
  flex: 1;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e8eb;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>