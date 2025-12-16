<template>
  <div class="layout-root">
    <header class="top-bar">
      <!-- 로고 -->
      <div class="logo-area">
        <img src="@/assets/logo/gaemi.png" class="logo-img" />
        <div class="logo-text">
          <div class="title">gAemI</div>
          <div class="subtitle">시간 없는 개미를 위한 AI 투자 파트너</div>
        </div>
      </div>

      <!-- 탭 -->
      <nav class="nav-tabs">
        <RouterLink
          to="/app/dashboard"
          class="tab"
          :class="{ active: $route.path.startsWith('/app/dashboard') }"
        >
          대시보드
        </RouterLink>

        <RouterLink
          to="/app/ai-news"
          class="tab"
          :class="{ active: $route.path.startsWith('/app/ai-news') }"
        >
          AI 뉴스 분석
        </RouterLink>

        <RouterLink
          to="/app/alerts"
          class="tab"
          :class="{ active: $route.path.startsWith('/app/alerts') }"
        >
          알림 관리
        </RouterLink>
      </nav>

      <!-- 오른쪽 영역 -->
      <div class="right-icons">
        <button class="icon-btn">🔔</button>
        <button class="icon-btn">⚙️</button>

        <!-- 로그인 안됨 -->
        <RouterLink v-if="!user" to="/login" class="login-btn">
          로그인
        </RouterLink>

        <!-- 로그인 됨 -->
        <div v-else class="user-area">
          <span class="username" @click="toggleDropdown">
            {{ user.nickname }}
          </span>

          <!-- ↓ 닉네임 클릭 시 나오는 박스 -->
          <div v-if="dropdownOpen" class="dropdown-box">
            <p class="nickname-display">@{{ user.username }}</p>
            <button class="logout-btn" @click="logout">로그아웃</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 컨텐츠 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView, RouterLink, useRouter } from "vue-router";
import { ref, onMounted } from "vue";

import { useFavoritesStore } from "@/stores/favoritesStore.js";

const favoritesStore = useFavoritesStore();

onMounted(() => {
  favoritesStore.loadFromLocal();
});


const router = useRouter();
const dropdownOpen = ref(false);
const user = ref(null);

/* ---------------------------
   로그인 정보 불러오기
--------------------------- */
onMounted(() => {
  const saved = localStorage.getItem("user");
  if (saved) {
    user.value = JSON.parse(saved);
  }
});

/* ---------------------------
   드롭다운 토글
--------------------------- */
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

/* ---------------------------
   로그아웃
--------------------------- */
const logout = () => {
  localStorage.removeItem("user");
  dropdownOpen.value = false;

  alert("로그아웃 되었습니다.");
  router.push("/login");
};
</script>

<style scoped>
.layout-root {
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  flex-direction: column;
}

/* 상단 바 */
.top-bar {
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 20;
}

/* 로고 */
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

/* 탭 */
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
  color: white !important;
}

/* 오른쪽 */
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
  border-radius: 6px;
}
.icon-btn:hover {
  background: #f3f4f6;
}

/* 로그인 버튼 */
.login-btn {
  padding: 6px 12px;
  background: #2563eb;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}
.login-btn:hover {
  background: #1d4ed8;
}

/* 사용자 영역 */
.user-area {
  position: relative;
  cursor: pointer;
}
.username {
  padding: 6px 10px;
  background: #eef2ff;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

/* 드롭다운 박스 */
.dropdown-box {
  position: absolute;
  top: 36px;
  right: 0;
  width: 140px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  z-index: 50;
}
.nickname-display {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}
.logout-btn {
  width: 100%;
  padding: 6px 0;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
}
.logout-btn:hover {
  background: #dc2626;
}

/* 컨텐츠 */
.main-content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 40px;
}
</style>
