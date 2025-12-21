import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "@/components/layout/MainLayout.vue";
import AuthLayout from "@/components/layout/AuthLayout.vue";

import WelcomePage from "@/pages/WelcomePage.vue";
import LoginPage from "@/pages/LoginPage.vue";
import SignupPage from "@/pages/SignupPage.vue";

import DashboardPage from "@/pages/DashboardPage.vue";
import AiNewsPage from "@/pages/AiNewsPage.vue";
import AlertSettingsPage from "@/pages/AlertSettingsPage.vue";
import ChatbotPage from "@/pages/ChatbotPage.vue";

const routes = [
  // ✅ 시작 페이지
  {
    path: "/",
    component: AuthLayout,
    children: [
      { path: "", component: WelcomePage },   // 👈 여기!
      { path: "welcome", component: WelcomePage },
      { path: "login", component: LoginPage },
      { path: "signup", component: SignupPage },
    ],
  },

  // ✅ 로그인 이후 앱
  {
    path: "/app",
    component: MainLayout,
    children: [
      { path: "dashboard", component: DashboardPage },
      { path: "ai-news", component: AiNewsPage },
      { path: "alerts", component: AlertSettingsPage },
      { path: "/app/chatbot", component: ChatbotPage, },
    ],
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
