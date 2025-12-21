<template>
  <div class="auth-page">
    <div class="auth-card small">
      <!-- 로고 -->
      <img src="@/assets/logo/gaemi.png" class="auth-logo" />

      <!-- 타이틀 -->
      <div class="header">
        <h1 class="title">로그인</h1>
        <p class="subtitle">시간 없는 개미를 위한 AI 투자 파트너</p>
      </div>

      <form class="form" @submit.prevent="onSubmit">
        <!-- 아이디 -->
        <div class="field">
          <label>아이디</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="아이디"
            required
          />
        </div>

        <!-- 비밀번호 -->
        <div class="field">
          <label>비밀번호</label>
          <div class="input-wrapper">
            <input
              :type="showPw ? 'text' : 'password'"
              v-model="form.password"
              placeholder="비밀번호"
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
              />
            </button>
          </div>
        </div>

        <button class="primary-btn">로그인</button>
      </form>

      <p class="footer-text">
        계정이 없으신가요?
        <span class="link" @click="goSignup">회원가입</span> |
        <span class="link" @click="goWelcome">메인으로</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";
import { useAlertEventsStore } from "@/stores/alertEventsStore";
import api from "@/api/axios";

const alertEventsStore = useAlertEventsStore();


const router = useRouter();
const showPw = ref(false);

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

// const mockUsers = [
//   { username: "gaemi", nickname: "개미봇", password: "1234" },
//   { username: "test", nickname: "관리자", password: "1234" },
// ];

const onSubmit = async () => {
  try {
    const res = await api.post("/users/login/", {
      username: form.value.username,
      password: form.value.password,
    });

    // 🔑 access token 저장
    const accessToken = res.data.access;
    const refreshToken = res.data.refresh;
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);

    // (선택) 로그인 상태 표시용 최소 정보
    localStorage.setItem(
      "user",
      JSON.stringify({
        username: form.value.username,
        isLogin: true,
      })
    );

    // ===============================
    // 🔔 [임시] 로그인 시 서버에서 내려온 알림 이벤트 mock
    // ===============================
    const mockAlertEvents = [
      {
        stockCode: "005930",
        stockName: "삼성전자",
        condition: "gte",
        target: 80000,
        currentPrice: 80100,
        triggeredAt: "2025-12-16T09:01:00",
      },
      {
        stockCode: "000660",
        stockName: "SK하이닉스",
        condition: "gte",
        target: 150000,
        currentPrice: 151200,
        triggeredAt: "2025-12-16T09:02:00",
      },
    ];

    mockAlertEvents.forEach(ev => {
      alertEventsStore.addEvent(ev);
    });

    alert("로그인 성공!");
    router.push("/app/dashboard");
  } catch (err) {
    console.error(err);
    alert("아이디 또는 비밀번호가 올바르지 않습니다.");
  }
};

const goSignup = () => router.push("/signup");
const goWelcome = () => router.push("/welcome");
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-card {
  width: 380px;
  background: white;
  padding: 36px 40px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
}

.auth-logo {
  width: 56px;
  margin: 0 auto 12px;
  display: block;
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.title {
  font-size: 26px;
  font-weight: 700;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  box-sizing: border-box;
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  padding-right: 44px;
}

.icon-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
}

.eye-icon {
  width: 20px;
}

.primary-btn {
  margin-top: 8px;
  width: 100%;
  background: #2563eb;
  color: white;
  padding: 12px 0;
  border-radius: 8px;
  border: none;
  font-weight: 600;
}

.footer-text {
  margin-top: 20px;
  text-align: center;
}

.link {
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
}
</style>
