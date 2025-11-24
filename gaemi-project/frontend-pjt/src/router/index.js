import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '@/components/layout/MainLayout.vue';

import DashboardPage from '@/pages/DashboardPage.vue';
import AiNewsPage from '@/pages/AiNewsPage.vue';
import AlertSettingsPage from '@/pages/AlertSettingsPage.vue';
import LoginPage from '@/pages/LoginPage.vue';

const routes = [
  // 🔹 레이아웃 없이 단독으로 뜨는 로그인 페이지
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },

  // 🔹 MainLayout을 사용하는 나머지 페이지들
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: DashboardPage },
      { path: 'ai-news', name: 'AiNews', component: AiNewsPage },
      { path: 'alerts', name: 'Alerts', component: AlertSettingsPage },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
