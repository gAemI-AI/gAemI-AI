import api from "@/api/axios";
import { useChatbotStore } from "@/stores/chatbotStore"; // ✅ 챗봇 스토어
import { useAlertsStore } from "@/stores/alertsStore";   // ✅ 알림 스토어
import { useFavoritesStore } from "@/stores/favoritesStore"; // ✅ 관심종목 스토어

export async function login(username, password) {
  const response = await api.post("/users/login/", { username, password });
  return response.data;
}

export async function logout() {
  // 1. 서버에 로그아웃 요청 (Refresh Token 무효화)
  const refreshToken = localStorage.getItem("refreshToken");
  if (refreshToken) {
    try {
      await api.post("/users/logout/", { refresh: refreshToken });
    } catch (e) {
      console.warn("Logout API Error:", e);
    }
  }

  // 2. 브라우저 저장소 삭제
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("user");

  // 3. ✅ [핵심] 핀이아(Pinia) 스토어 데이터 초기화
  const chatbotStore = useChatbotStore();
  const alertsStore = useAlertsStore();
  const favoritesStore = useFavoritesStore();

  chatbotStore.clearMessages(); // 👈 이게 실행돼야 챗봇이 초기화됨
  alertsStore.clearAlerts();
  favoritesStore.$reset();      // 혹은 favoritesStore.favorites = []
}
