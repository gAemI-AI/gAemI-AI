<template>
  <div class="layout-root">
    <!-- 상단 바 -->
    <header class="top-bar">
      <!-- 왼쪽 로고 -->
      <div class="logo-area">
        <img src="@/assets/logo/gaemi.png" class="logo-img" />
        <div class="logo-text">
          <div class="title">gAemI</div>
          <div class="subtitle">실시간 종목 모니터링</div>
        </div>
      </div>

      <!-- 중앙 탭 -->
      <nav class="nav-tabs">
        <RouterLink
          to="/dashboard"
          class="tab"
          :class="{ active: $route.path === '/dashboard' }"
        >
          대시보드
        </RouterLink>
        <RouterLink
          to="/ai-news"
          class="tab"
          :class="{ active: $route.path === '/ai-news' }"
        >
          AI 뉴스 분석
        </RouterLink>
        <RouterLink
          to="/alerts"
          class="tab"
          :class="{ active: $route.path === '/alerts' }"
        >
          알림 관리
        </RouterLink>
      </nav>

      <!-- 오른쪽 아이콘 + 로그인 -->
      <div class="right-icons">
        <button class="icon-btn">🔔</button>
        <button class="icon-btn">⚙️</button>

        <RouterLink to="/login" class="login-btn">
          로그인
        </RouterLink>
      </div>
    </header>

    <!-- 페이지 공통 박스 -->
    <main class="main-content">
      <!-- 🔹 예전의 <slot /> 대신 여기에서 자식 라우트 렌더링 -->
      <RouterView />
    </main>

    <!-- 🔹 어디서나 열리는 토스트 + 챗봇 (레이아웃 안으로 이동) -->
    <AlertToast
      v-if="showSampleToast"
      :type="'warning'"
      title="실시간 시장 급등 알림"
      message="삼성전자에 중요한 속보가 발생했습니다. 상세 내용은 AI 뉴스 분석 탭에서 확인하세요."
    />
    <AiChatWidget />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { ref, onMounted } from 'vue';
import AiChatWidget from '@/components/chat/AiChatWidget.vue';
import AlertToast from '@/components/alerts/AlertToast.vue';

const showSampleToast = ref(false);

onMounted(() => {
  setTimeout(() => {
    showSampleToast.value = true;
    setTimeout(() => (showSampleToast.value = false), 5000);
  }, 2000);
});
</script>

<style scoped>
.layout-root {
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  flex-direction: column;
}

/* 상단 바 (너가 쓰던 버전 유지) */
.top-bar {
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}

.logo-area {
  position: absolute;
  left: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-text .title {
  font-weight: 700;
  font-size: 18px;
}
.logo-text .subtitle {
  font-size: 12px;
  color: #6b7280;
}

.nav-tabs {
  display: flex;
  gap: 16px;
  justify-content: center;
  width: 1400px;
}

.tab {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 14px;
  color: #6b7280;
  text-decoration: none;
}
.tab.active {
  background: #2563eb;
  color: white;
}

.right-icons {
  position: absolute;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
  padding: 6px;
}
.icon-btn:hover {
  background: #f3f4f6;
  border-radius: 6px;
}

.login-btn {
  padding: 6px 12px;
  background: #2563eb;
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.login-btn:hover {
  background: #1d4ed8;
}

/* 회색 박스 크기 그대로 유지 */
.main-content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 40px;
}
</style>
