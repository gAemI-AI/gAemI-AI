<template>
  <MainLayout>
    <router-view />

    <!-- 우측 하단 알림 토스트 (예시 1개) -->
    <AlertToast
      v-if="showSampleToast"
      :type="'warning'"
      title="실시간 시장 급등 알림"
      message="삼성전자에 중요한 속보가 발생했습니다. 상세 내용은 AI 뉴스 분석 탭에서 확인하세요."
    />

    <!-- 어디서나 열리는 AI 챗봇 -->
    <AiChatWidget />
  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import MainLayout from './components/layout/MainLayout.vue';
import AiChatWidget from './components/chat/AiChatWidget.vue';
import AlertToast from './components/alerts/AlertToast.vue';

const showSampleToast = ref(false);

onMounted(() => {
  // 예시로 2초 뒤에 알림 한 번 띄우기
  setTimeout(() => {
    showSampleToast.value = true;
    setTimeout(() => (showSampleToast.value = false), 5000);
  }, 2000);
});
</script>

<!-- <script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style> -->
