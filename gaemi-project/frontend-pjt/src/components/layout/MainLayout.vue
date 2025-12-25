<template>
  <div class="layout-root">
    <header class="top-bar">
      <div class="header-inner">
        
        <RouterLink to="/app/dashboard" class="logo-area">
          <img src="@/assets/logo/gaemi.png" class="logo-img" alt="logo" />
          <span class="brand-name">gAemI</span>
        </RouterLink>

        <nav class="nav-menu" ref="navMenuRef">
          <RouterLink
            to="/app/dashboard"
            class="nav-item"
            :class="{ active: route.path.startsWith('/app/dashboard') }"
          >
            대시보드
          </RouterLink>

          <RouterLink
            to="/app/chatbot"
            class="nav-item"
            :class="{ active: route.path.startsWith('/app/chatbot') }"
          >
            AI 챗봇
          </RouterLink>

          <RouterLink
            to="/app/alerts"
            class="nav-item"
            :class="{ active: route.path.startsWith('/app/alerts') }"
          >
            알림 관리
          </RouterLink>
          
          <div class="nav-highlighter" :style="highlighterStyle"></div>
        </nav>

        <div class="right-tools">
          
          <div class="bell-wrapper">
            <button class="icon-btn" @click="bellOpen = !bellOpen">
              <span v-if="alertEventsStore.count > 0" class="bell-dot"></span>
              <img src="@/assets/icons/bell.png" alt="알림" class="bell-icon" />
            </button>

            <transition name="fade">
              <div v-if="bellOpen" class="alert-dropdown">
                <div class="alert-head">
                  <span class="title">알림</span>
                  <span class="count">{{ alertEventsStore.count }}</span>
                </div>
                <div class="alert-list" v-if="alertEventsStore.latestEvents.length > 0">
                  <div
                    v-for="ev in alertEventsStore.latestEvents.slice(0, 20)"
                    :key="ev.id"
                    class="alert-item"
                    @click="bellOpen = false"
                  >
                    <div class="alert-content">
                      <span class="stock-name">{{ ev.stockName }}</span>
                      <span class="alert-desc">
                        {{ formatCondition(ev.condition, ev.target) }} 조건 도달
                      </span>
                    </div>
                    <span class="alert-time">{{ formatTime(ev.triggeredAt) }}</span>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <div class="empty-text">새로운 알림이 없습니다</div>
                </div>
              </div>
            </transition>
          </div>

          <div v-if="user" class="user-profile" @click="toggleDropdown">
            <div class="avatar-circle">{{ user.nickname[0] }}</div>
            <span class="username">{{ user.nickname }}</span>
            
            <transition name="fade">
              <div v-if="dropdownOpen" class="profile-dropdown">
                <div class="profile-info">
                  <span class="info-name">{{ user.nickname }}</span>
                  <span class="info-id">@{{ user.username }}</span>
                </div>
                <div class="divider"></div>
                <button class="menu-item logout" @click.stop="logout">로그아웃</button>
              </div>
            </transition>
          </div>

          <RouterLink v-else to="/login" class="login-link">
            로그인
          </RouterLink>
        </div>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>

  <ToastStack v-if="showToastsHere && toastStore.toasts.length > 0" />
  <ChatbotFab />
  <ChatbotPanel v-if="chatbotStore.isOpen" />
</template>

<script setup>
import { RouterView, RouterLink, useRouter, useRoute } from "vue-router";
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";
import { useChatbotStore } from "@/stores/chatbotStore";
import { useToastStore } from "@/stores/toastStore";
import { useAlertEventsStore } from "@/stores/alertEventsStore";

import ChatbotFab from "@/components/chat/ChatbotFab.vue";
import ChatbotPanel from "@/components/chat/ChatbotPanel.vue";
import ToastStack from "@/components/toast/ToastStack.vue";

/* Stores & Router */
const favoritesStore = useFavoritesStore();
const chatbotStore = useChatbotStore();
const toastStore = useToastStore();
const alertEventsStore = useAlertEventsStore();
const router = useRouter();
const route = useRoute();

/* UI State */
const dropdownOpen = ref(false);
const user = ref(null);
const bellOpen = ref(false);

/* =========================================
   ✅ 슬라이딩 메뉴바 로직
========================================= */
const navMenuRef = ref(null);
const highlighterStyle = ref({
  left: "0px",
  width: "0px",
  opacity: 0,
});

const updateHighlighter = async () => {
  await nextTick();
  if (!navMenuRef.value) return;

  const activeLink = navMenuRef.value.querySelector(".nav-item.active");

  if (activeLink) {
    const menuRect = navMenuRef.value.getBoundingClientRect();
    const linkRect = activeLink.getBoundingClientRect();

    highlighterStyle.value = {
      left: `${linkRect.left - menuRect.left}px`,
      width: `${linkRect.width}px`,
      opacity: 1,
    };
  } else {
    highlighterStyle.value = { ...highlighterStyle.value, opacity: 0 };
  }
};

watch(() => route.path, updateHighlighter, { immediate: true });

onMounted(() => {
  window.addEventListener("resize", updateHighlighter);
});
onUnmounted(() => {
  window.removeEventListener("resize", updateHighlighter);
});

/* =========================================
   기타 로직 (토스트, 알림 등)
========================================= */
const showToastsHere = computed(() => {
  const p = route.path;
  return (
    p.startsWith("/app/dashboard") ||
    p.startsWith("/app/chatbot") ||
    p.startsWith("/app/alerts")
  );
});

const lastToastKey = computed(() => {
  const username = user.value?.username;
  return username ? `last_toast_at_${username}` : null;
});

/* =========================================
   기타 로직 (토스트, 알림 등)
========================================= */
// ... (showToastsHere, lastToastKey 등 기존 코드 유지) ...

// 🛠️ [수정] 토스트 메시지 생성 함수
function toastFromEvent(ev) {
  // 숫자에 콤마 추가
  const val = Number(ev.target).toLocaleString();
  let condText = "";
  let unit = "원";

  // 조건 문구 설정
  if (ev.condition === "gte" || ev.condition === "PRICE_ABOVE") {
    condText = "이상";
  } else if (ev.condition === "lte" || ev.condition === "PRICE_BELOW") {
    condText = "이하";
  } else if (ev.condition === "changeUp") {
    condText = "이상 상승";
    unit = "%";
  } else if (ev.condition === "changeDown") {
    condText = "이상 하락";
    unit = "%";
  }

  return {
    type: "info",
    title: "🔔 알림 도착",
    // 목표: "삼성전자 110,000원 이상 달성!"
    message: `${ev.stockName} ${val}${unit} ${condText} 달성!`,
  };
}

// 🛠️ [수정] 알림 드롭다운용 텍스트 포맷
function formatCondition(condition, target) {
  const val = Number(target).toLocaleString();
  switch (condition) {
    case "gte": return `${val}원 이상`;
    case "lte": return `${val}원 이하`;
    case "changeUp": return `${val}% 이상 급등`;
    case "changeDown": return `${val}% 이상 급락`;
    default: return "";
  }
}

// ... (나머지 formatTime, flushUnshownEvents 등은 그대로 유지) ...

function formatTime(iso) {
  const d = new Date(iso);
  const now = new Date();
  const diff = (now - d) / 1000 / 60;
  if (diff < 1) return "방금 전";
  if (diff < 60) return `${Math.floor(diff)}분 전`;
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function flushUnshownEvents() {
  if (!user.value?.isLogin) return;
  if (!lastToastKey.value) return;

  const lastShownAt = localStorage.getItem(lastToastKey.value);
  const myEvents = alertEventsStore.latestEvents;
  const newOnes = myEvents.filter((ev) => {
    if (!lastShownAt) return true;
    return new Date(ev.triggeredAt) > new Date(lastShownAt);
  });

  newOnes
    .slice()
    .sort((a, b) => new Date(a.triggeredAt) - new Date(b.triggeredAt))
    .forEach((ev) => toastStore.push(toastFromEvent(ev)));

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
  chatbotStore.loadFromLocal();

  if (chatbotStore.messages.length > 0 && route.path.startsWith("/app/chatbot")) {
    chatbotStore.isOpen = true;
  }
  flushUnshownEvents();
});

watch(() => alertEventsStore.events.length, () => {
  flushUnshownEvents();
});

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const logout = () => {
  localStorage.removeItem("user");
  dropdownOpen.value = false;
  router.push("/login");
};

function closeBell(e) {
  if (e.target.closest(".alert-dropdown")) return;
  if (e.target.closest(".bell-wrapper")) return;
  if (e.target.closest(".user-profile")) return;
  
  bellOpen.value = false;
  dropdownOpen.value = false;
}

onMounted(() => {
  document.addEventListener("click", closeBell);
});

onUnmounted(() => {
  document.removeEventListener("click", closeBell);
});
</script>

<style scoped>
/* =========================
   Layout & Reset
========================== */
.layout-root {
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
}

/* =========================
   Top Bar (Header)
========================== */
.top-bar {
  height: 60px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: center;
}

.header-inner {
  width: 100%;
  max-width: 1400px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

/* 1. Logo */
.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  cursor: pointer;
}

.logo-img {
  width: 28px;
  height: 28px;
}

.brand-name {
  font-size: 20px;
  font-weight: 800;
  color: #191f28;
  letter-spacing: -0.5px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* =========================
   2. Navigation
========================== */
.nav-menu {
  display: flex;
  gap: 2px;
  position: relative;
  height: 100%;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-size: 17px;
  font-weight: 600;
  color: #8b95a1;
  text-decoration: none;
  transition: color 0.2s ease;
  position: relative;
  height: 100%;
}

.nav-item:hover {
  color: #4e5968;
}

.nav-item.active {
  color: #3182f6;
}

.nav-highlighter {
  position: absolute;
  bottom: 0;
  height: 3px;
  background-color: #3182f6;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  pointer-events: none;
}


/* 3. Right Tools */
.right-tools {
  display: flex;
  align-items: center;
  gap: 16px;
}

.bell-wrapper {
  position: relative;
}

.icon-btn {
  background: none;
  border: none;
  /* font-size: 20px; 제거: 이미지로 대체 */
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #f2f4f6;
}

/* ✅ 종 아이콘 이미지 스타일 */
.bell-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  display: block;
}

.bell-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 5px;
  height: 5px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
}

/* 알림 드롭다운 */
.alert-dropdown {
  position: absolute;
  top: 50px;
  right: -10px;
  width: 320px;
  background: white;
  border: 1px solid #e5e8eb;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  z-index: 100;
}

.alert-head {
  padding: 16px;
  border-bottom: 1px solid #f2f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-head .title {
  font-weight: 700;
  color: #191f28;
}

.alert-head .count {
  font-size: 12px;
  background: #3182f6;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.alert-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  padding: 14px 16px;
  border-bottom: 1px solid #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: background 0.2s;
  cursor: pointer;
}

.alert-item:hover {
  background: #f9fafb;
}

.alert-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-name {
  font-weight: 700;
  font-size: 14px;
  color: #333;
}

.alert-desc {
  font-size: 13px;
  color: #6b7684;
}

.alert-time {
  font-size: 11px;
  color: #adb5bd;
  white-space: nowrap;
  margin-top: 2px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}
.empty-text {
  font-size: 14px;
  color: #8b95a1;
}

/* User Profile */
.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.2s;
  position: relative;
}

.user-profile:hover {
  background: #f2f4f6;
}

.avatar-circle {
  width: 30px;
  height: 30px;
  background: #3182f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

/* Profile Dropdown */
.profile-dropdown {
  position: absolute;
  top: 50px;
  right: 0;
  width: 200px;
  background: white;
  border: 1px solid #e5e8eb;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 8px;
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.profile-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-name {
  font-weight: 700;
  color: #191f28;
  font-size: 16px;
}

.info-id {
  font-size: 13px;
  color: #8b95a1;
}

.divider {
  height: 1px;
  background: #f2f4f6;
  margin: 4px 0;
}

.menu-item {
  text-align: left;
  background: none;
  border: none;
  padding: 12px;
  font-size: 15px;
  color: #4e5968;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #f2f4f6;
}

.menu-item.logout {
  color: #f04452;
}

/* Login Link */
.login-link {
  font-size: 15px;
  font-weight: 600;
  color: #3182f6;
  text-decoration: none;
  padding: 8px 16px;
  background: rgba(49, 130, 246, 0.1);
  border-radius: 8px;
  transition: background 0.2s;
}

.login-link:hover {
  background: rgba(49, 130, 246, 0.15);
}

/* Main Content */
.main-content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  flex: 1;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>