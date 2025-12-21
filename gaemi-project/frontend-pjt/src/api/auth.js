// src/api/auth.js
import api from "@/api/axios";

export async function logout() {
  const refreshToken = localStorage.getItem("refreshToken");

  // refreshToken이 있으면 서버에 무효화 요청
  if (refreshToken) {
    try {
      await api.post("/users/logout/", { refresh: refreshToken });
    } catch (e) {
      // 서버 요청 실패해도 프론트는 로그아웃 처리 진행 (MVP)
      console.warn("logout api failed:", e);
    }
  }

  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("user");
}
