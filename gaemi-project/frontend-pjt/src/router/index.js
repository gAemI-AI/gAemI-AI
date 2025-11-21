import { createRouter, createWebHistory } from 'vue-router';
import DashboardPage from '@/pages/DashboardPage.vue';
import AiNewsPage from '@/pages/AiNewsPage.vue';
import AlertSettingsPage from '@/pages/AlertSettingsPage.vue';

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: DashboardPage },
  { path: '/ai-news', name: 'AiNews', component: AiNewsPage },
  { path: '/alerts', name: 'Alerts', component: AlertSettingsPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
