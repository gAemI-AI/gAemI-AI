<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="logo-wrapper">
        <img src="@/assets/logo/gaemi.png" class="auth-logo" alt="logo" />
      </div>

      <div class="header">
        <h1 class="title">로그인</h1>
        <p class="subtitle">gAemI와 함께 투자 여정을 시작하세요</p>
      </div>

      <form class="form" @submit.prevent="onSubmit">
        <div class="field">
          <label>아이디</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="아이디를 입력해주세요"
            required
          />
        </div>

        <div class="field">
          <label>비밀번호</label>
          <div class="input-wrapper">
            <input
              :type="showPw ? 'text' : 'password'"
              v-model="form.password"
              placeholder="비밀번호를 입력해주세요"
              required
            />
            <button
              type="button"
              class="icon-btn"
              @click="showPw = !showPw"
            >
              <img
                :src="showPw ? eyeClosed : eyeOpen"
                class="eye-icon"
                alt="toggle password"
              />
            </button>
          </div>
        </div>

        <button class="primary-btn">로그인</button>
      </form>

      <div class="footer-area">
        <p class="footer-text">
          계정이 없으신가요? <span class="link" @click="goSignup">회원가입</span>
        </p>
        <p class="footer-secondary">
          <span class="link" @click="goWelcome">메인으로 돌아가기</span>
        </p>
      </div>
    </div>

    <transition name="modal-fade">
      <div v-if="showSuccessModal" class="modal-overlay">
        <div class="success-modal">
          <div class="modal-icon">✓</div>
          <h2 class="modal-title">로그인 성공!</h2>
          <p class="modal-subtitle">{{ form.username }}님, 환영합니다</p>
          <p class="modal-loading">잠시만 기다려주세요...</p>
          <div class="spinner"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";

// 이미지 에셋
import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";

// API 및 Store
import { login } from "@/api/auth";
import { useChatbotStore } from "@/stores/chatbotStore";
import { useAlertsStore } from "@/stores/alertsStore";
import { useFavoritesStore } from "@/stores/favoritesStore";

const router = useRouter();
const chatbotStore = useChatbotStore();
const alertsStore = useAlertsStore();
const favoritesStore = useFavoritesStore();

const showPw = ref(false);
const showSuccessModal = ref(false);

const form = ref({
  username: "",
  password: "",
});

/* 한글 → 영문 자동 변환 */
const hangulToEngMap = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t',
  'ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g',
  'ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b',
  'ㅜ':'n','ㅡ':'m'
};

watch(
  () => form.value.password,
  (val) => {
    const converted = val
      .split("")
      .map(ch => hangulToEngMap[ch] || ch)
      .join("");
    if (converted !== val) form.value.password = converted;
  }
);

/* ✅ 안전장치: 로그인 페이지 진입 시 모든 이전 데이터 삭제 */
onMounted(() => {
  // 1. 챗봇 대화내용 삭제
  chatbotStore.clearMessages();
  
  // 2. 알림 목록 비우기
  alertsStore.clearAlerts();
  
  // 3. 관심종목 비우기
  favoritesStore.favorites = []; 

  // 4. 로컬 스토리지에 남은 인증 정보 삭제
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("user");
});

/* 로그인 제출 함수 */
const onSubmit = async () => {
  try {
    const data = await login(form.value.username, form.value.password);
    const user = data.user;

    // 사용자 정보와 토큰 저장
    localStorage.setItem(
      "user",
      JSON.stringify({
        id: user.id,
        username: user.username,
        nickname: user.nickname,
        email: user.email,
        isLogin: true,
      })
    );
    
    localStorage.setItem("accessToken", data.access);
    localStorage.setItem("refreshToken", data.refresh);

    // 성공 팝업 표시
    showSuccessModal.value = true;

    // 2초 후 대시보드로 이동
    setTimeout(() => {
      router.push("/app/dashboard");
    }, 2000);

  } catch (error) {
    console.error("로그인 오류:", error);
    const errorMsg = error.response?.data?.error || 
                     error.response?.data?.detail || 
                     "로그인 정보를 확인해주세요.";
    alert(errorMsg);
  }
};

const goSignup = () => router.push("/signup");
const goWelcome = () => router.push("/welcome");
</script>

<style scoped>
/* ======================= */
/* 페이지 레이아웃     */
/* ======================= */
.auth-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

/* ======================= */
/* 카드 디자인         */
/* ======================= */
.auth-card {
  width: 100%;
  max-width: 480px;
  background: white;
  padding: 48px 64px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

/* 로고 래퍼 */
.logo-wrapper {
  margin-bottom: 28px;
  text-align: center;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

.auth-logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

/* 헤더 */
.header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #111827;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
}

/* ======================= */
/* 폼 디자인           */
/* ======================= */
.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 24px;
}

/* 필드 */
.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field label {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  letter-spacing: -0.3px;
}

input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  box-sizing: border-box;
  font-size: 15px;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

input::placeholder {
  color: #9ca3af;
}

/* 입력 래퍼 */
.input-wrapper {
  position: relative;
}

.input-wrapper input {
  padding-right: 44px;
}

/* 아이콘 버튼 */
.icon-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  transition: opacity 0.2s ease;
}

.icon-btn:hover {
  opacity: 0.7;
}

.eye-icon {
  width: 20px;
  height: 20px;
}

/* CTA 버튼 */
.primary-btn {
  width: 100%;
  padding: 14px 0;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

.primary-btn:active {
  transform: translateY(0);
}

/* ======================= */
/* 푸터                */
/* ======================= */
.footer-area {
  text-align: center;
}

.footer-text {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  letter-spacing: -0.2px;
}

.footer-secondary {
  margin-top: 12px;
  font-size: 13px;
  color: #9ca3af;
  letter-spacing: -0.2px;
}

.link {
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease;
}

.link:hover {
  color: #1d4ed8;
}

/* 모바일 반응형 */
@media (max-width: 480px) {
  .auth-card {
    padding: 32px 24px;
  }
  .title {
    font-size: 26px;
  }
  .subtitle {
    font-size: 13px;
  }
}

/* ======================= */
/* 성공 모달 팝업        */
/* ======================= */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.success-modal {
  background: white;
  border-radius: 20px;
  padding: 48px 40px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  max-width: 360px;
  width: 90%;
  animation: modalBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalBounce {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-icon {
  width: 80px; height: 80px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 24px;
  font-size: 48px; color: white; font-weight: 700;
  animation: iconScale 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes iconScale {
  0% { transform: scale(0); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.modal-title {
  font-size: 28px; font-weight: 700; margin: 0 0 12px 0; color: #111827; letter-spacing: -0.5px;
}

.modal-subtitle {
  font-size: 15px; color: #6b7280; margin: 0 0 20px 0; font-weight: 400;
}

.modal-loading {
  font-size: 14px; color: #9ca3af; margin: 0 0 16px 0; font-weight: 500;
}

.spinner {
  width: 40px; height: 40px;
  border: 3px solid #e5e7eb; border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
</style>