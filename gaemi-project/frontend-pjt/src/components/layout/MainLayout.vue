<template>
    <!-- =========================
         기존 레이아웃 (원본 유지)
    ========================== -->
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

          <!-- <RouterLink
            to="/app/ai-news"
            class="tab"
            :class="{ active: $route.path.startsWith('/app/ai-news') }"
          >
            AI 뉴스 분석
          </RouterLink> -->
          
          <RouterLink
            to="/app/chatbot"
            class="tab"
            :class="{ active: $route.path.startsWith('/app/chatbot') }"
          >
            AI 챗봇
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
          <button class="icon-btn bell-btn" @click="bellOpen = !bellOpen">🔔</button>
          <div v-if="bellOpen" class="alert-dropdown">
            <!-- 헤더 -->
            <div class="alert-head">
              <span class="title">알림</span>
              <span class="count">{{ alertEventsStore.count }}개</span>
            </div>

            <!-- 리스트 -->
            <div class="alert-list" v-if="alertEventsStore.latestEvents.length > 0">
              <div
                v-for="ev in alertEventsStore.latestEvents.slice(0, 20)"
                :key="ev.id"
                class="alert-item"
              >
                <div class="alert-main">
                  <span class="stock">{{ ev.stockName }}</span>
                  <span class="msg">
                    {{ formatCondition(ev.condition, ev.target) }}
                  </span>
                </div>
                <div class="time">{{ formatTime(ev.triggeredAt) }}</div>
              </div>
            </div>

            <!-- 비었을 때 -->
            <div v-else class="empty">
              아직 알림이 없어요.
            </div>
          </div>

          <!-- 로그인 안됨 -->
          <RouterLink v-if="!user" to="/login" class="login-btn">
            로그인
          </RouterLink>

          <!-- 로그인 됨 -->
          <div v-else class="user-area">
            <span class="username" @click="toggleDropdown">
              {{ user.nickname }}
            </span>

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

    <!-- =========================
         전역 UI (layout-root 밖)
    ========================== -->
    <ToastStack v-if="showToastsHere && toastStore.toasts.length > 0" />
    <ChatbotFab />
    <ChatbotPanel v-if="chatbotStore.isOpen" />

</template>

<script setup>
import { RouterView, RouterLink, useRouter, useRoute } from "vue-router";
import { ref, onMounted, onUnmounted, watch, computed } from "vue";

import { useFavoritesStore } from "@/stores/favoritesStore.js";
import { useChatbotStore } from "@/stores/chatbotStore";
import { useToastStore } from "@/stores/toastStore";

import { useAlertEventsStore } from "@/stores/alertEventsStore";

import ChatbotFab from "@/components/chat/ChatbotFab.vue";
import ChatbotPanel from "@/components/chat/ChatbotPanel.vue";
import ToastStack from "@/components/toast/ToastStack.vue";

const favoritesStore = useFavoritesStore();
const chatbotStore = useChatbotStore();
const toastStore = useToastStore();

const alertEventsStore = useAlertEventsStore();

const router = useRouter();
const route = useRoute();

const dropdownOpen = ref(false);
const user = ref(null);
const bellOpen = ref(false);

/** ✅ 토스트를 보여줄 페이지 제한
 * - /app/dashboard, /app/chatbot, /app/alerts 에서만 토스트 표시
 */
const showToastsHere = computed(() => {
  const p = route.path;
  return (
    p.startsWith("/app/dashboard") ||
    p.startsWith("/app/chatbot") ||
    p.startsWith("/app/alerts")
  );
});

/** ✅ (핵심) user별 마지막 토스트 처리 시점 저장 키 */
const lastToastKey = computed(() => {
  const username = user.value?.username;
  return username ? `last_toast_at_${username}` : null;
});

/** ✅ 이벤트 1개를 토스트로 변환 */
function toastFromEvent(ev) {
  return {
    type: "info",
    title: "알림 도착",
    // event 구조에 맞춰 메시지 구성 (현재 alertEventsStore 예시 기반)
    message: `${ev.stockName} · ${ev.target}${ev.condition === "changeUp" || ev.condition === "changeDown" ? "%" : "원"} 조건 충족`,
  };
}
function formatCondition(condition, target) {
  switch (condition) {
    case "gte":
      return `${target}원 이상`;
    case "lte":
      return `${target}원 이하`;
    case "changeUp":
      return `${target}% 이상`;
    case "changeDown":
      return `${target}% 이하`;
    default:
      return "";
  }
}

function formatTime(iso) {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
}

/** ✅ 로그인 직후/새 이벤트 도착 시, "안 띄운 이벤트만" 토스트로 띄우기 */
function flushUnshownEvents() {
  if (!user.value?.isLogin) return;                 // 로그인 상태 아니면 토스트 X
  if (!lastToastKey.value) return;

  const lastShownAt = localStorage.getItem(lastToastKey.value); // ISO string or null

  // 내 이벤트만 (나중에 서버 붙이면 event에 username/userId 필수)
  const myEvents = alertEventsStore.latestEvents;

  const newOnes = myEvents.filter((ev) => {
    if (!lastShownAt) return true;
    // triggeredAt이 lastShownAt 이후인 것만
    return new Date(ev.triggeredAt) > new Date(lastShownAt);
  });

  // 오래된 것부터 순서대로 토스트 띄우기 (FIFO 자연스럽게)
  newOnes
    .slice()
    .sort((a, b) => new Date(a.triggeredAt) - new Date(b.triggeredAt))
    .forEach((ev) => toastStore.push(toastFromEvent(ev)));

  // 마지막으로 처리한 시점 갱신 (가장 최신 이벤트 기준)
  if (newOnes.length > 0) {
    const newest = newOnes.reduce((acc, cur) =>
      new Date(cur.triggeredAt) > new Date(acc.triggeredAt) ? cur : acc
    );
    localStorage.setItem(lastToastKey.value, newest.triggeredAt);
  }
}

onMounted(() => {
  favoritesStore.loadFromLocal();

  const saved = localStorage.getItem("user");
  if (saved) user.value = JSON.parse(saved);

  // ✅ 로그인 후 들어왔을 때: "쌓인 알림" 토스트로 한번에 처리
  flushUnshownEvents();
});

// ✅ 새 이벤트가 들어올 때마다 토스트 처리
watch(
  () => alertEventsStore.events.length,
  () => {
    flushUnshownEvents();
  }
);

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const logout = () => {
  localStorage.removeItem("user");
  dropdownOpen.value = false;
  alert("로그아웃 되었습니다.");
  router.push("/login");
};

function closeBell(e) {
  // 클릭한 곳이 종버튼/드롭다운 내부면 닫지 않음
  if (e.target.closest(".alert-dropdown")) return;
  if (e.target.closest(".bell-btn")) return;

  bellOpen.value = false;
}

onMounted(() => {
  document.addEventListener("click", closeBell);
});

onUnmounted(() => {
  document.removeEventListener("click", closeBell);
});

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
  width: 100%;
  max-width: 1400px;
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
  box-sizing: border-box;
}
/* 🔔 알림 드롭다운 */
.alert-dropdown {
  position: absolute;
  top: 44px;          /* 종 버튼 바로 아래 */
  right: 0;
  width: 320px;
  max-height: 420px;

  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);

  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 100;
}

/* 헤더 */
.alert-head {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-weight: 600;
}

.alert-head .title {
  font-size: 14px;
}

.alert-head .count {
  font-size: 12px;
  color: #2563eb;
}

/* 리스트 */
.alert-list {
  overflow-y: auto;
}

/* 개별 알림 */
.alert-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
}

.alert-item:hover {
  background: #f8fafc;
}

.alert-main {
  display: flex;
  gap: 6px;
  align-items: center;
}

.stock {
  font-size: 12px;
  font-weight: 600;
  color: #2563eb;
  background: #eef2ff;
  padding: 2px 6px;
  border-radius: 6px;
}

.msg {
  font-size: 13px;
  color: #374151;
}

.time {
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}

/* 비었을 때 */
.empty {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: #9ca3af;
}

</style>
