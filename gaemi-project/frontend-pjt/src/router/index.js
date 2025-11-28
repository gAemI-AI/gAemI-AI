import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "@/components/layout/MainLayout.vue";

// 단독 페이지
import WelcomePage from "@/pages/WelcomePage.vue";
import LoginPage from "@/pages/LoginPage.vue";
import SignupPage from "@/pages/SignupPage.vue";

// MainLayout 페이지
import DashboardPage from "@/pages/DashboardPage.vue";
import AiNewsPage from "@/pages/AiNewsPage.vue";
import AlertSettingsPage from "@/pages/AlertSettingsPage.vue";

const routes = [
  { path: "/", redirect: "/welcome" },

  { path: "/welcome", component: WelcomePage },
  { path: "/login", component: LoginPage },
  { path: "/signup", component: SignupPage },

  {
    path: "/app",
    component: MainLayout, // 여기서만 상단바 렌더링됨
    children: [
      { path: "dashboard", component: DashboardPage },
      { path: "ai-news", component: AiNewsPage },
      { path: "alerts", component: AlertSettingsPage },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
