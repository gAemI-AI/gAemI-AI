<template>
  <div class="layout-root">
    <!-- 상단 바 -->
    <header class="top-bar">
      <div class="logo-area">
        <div class="logo-icon">🦗</div>
        <div class="logo-text">
          <div class="title">gAemI</div>
          <div class="subtitle">실시간 종목 모니터링</div>
        </div>
      </div>

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

      <div class="right-icons">
        <button class="icon-btn">🔔</button>
        <button class="icon-btn">⚙️</button>
      </div>
    </header>

    <!-- 모든 페이지 공통 박스 -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout-root {
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  flex-direction: column;
}

/* ⭐ 상단 페이지 버튼 중앙 고정 */
.top-bar {
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: center; /* 전체 중앙 기준 */
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}

/* 왼쪽 로고와 오른쪽 아이콘은 절대 위치로 고정 */
.logo-area {
  position: absolute;
  left: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.right-icons {
  position: absolute;
  right: 32px;
  display: flex;
  gap: 8px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.logo-text .title {
  font-weight: 700;
  font-size: 18px;
}
.logo-text .subtitle {
  font-size: 12px;
  color: #6b7280;
}

/* ⭐ 탭 영역은 항상 콘텐츠 박스 안에서 가로 중앙 */
.nav-tabs {
  display: flex;
  gap: 16px;
  justify-content: center;
  width: 1400px; /* 대시보드 기준 고정 */
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

/* ⭐ 연회색 박스 크기 통일 */
.main-content {
  width: 100%;
  max-width: 1400px;   /* 통일된 박스 크기 */
  margin: 0 auto;
  padding: 20px 40px;  /* 페이지 내부 여백 동일 */
}
</style>

