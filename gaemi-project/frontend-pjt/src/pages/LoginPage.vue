<template>
  <div class="auth-page">
    <div class="auth-card small">
      <img src="@/assets/logo/gaemi.png" class="auth-logo" />
      <h1 class="title">로그인</h1>
      <p class="subtitle">시간 없는 개미를 위한 AI 투자 파트너</p>

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
        <div class="input-row">
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
import { ref } from "vue";
import { useRouter } from "vue-router";

import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";

import { watch } from "vue";

/* 한글 → 영문 매핑 */
const hangulToEngMap = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t',
  'ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g',
  'ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b',
  'ㅜ':'n','ㅡ':'m'
};

function convertHangulToEng(input) {
  return input
    .split("")
    .map(ch => hangulToEngMap[ch] || ch)
    .join("");
}


const router = useRouter();
const showPw = ref(false);

const form = ref({
  username: "",
  password: "",
});

watch(
  () => form.value.password,
  (val) => {
    const converted = convertHangulToEng(val || "");
    if (converted !== val) {
      form.value.password = converted;
    }
  }
);
/* 임시 유저 데이터 - 회원가입 기능 연결 전까지 사용 */
const mockUsers = [
  { username: "gaemi", nickname: "개미봇", password: "1234" },
  { username: "test", nickname: "주연", password: "1234" },
];

/* 로그인 */
const onSubmit = () => {
  const user = mockUsers.find(
    (u) =>
      u.username === form.value.username &&
      u.password === form.value.password
  );

  if (!user) {
    alert("아이디 또는 비밀번호가 올바르지 않습니다.");
    return;
  }

  /* --------------------------
      로그인 상태 저장 (중요)
      MainLayout에서 읽기 위한 구조
  ---------------------------*/
  localStorage.setItem(
    "user",
    JSON.stringify({
      username: user.username,
      nickname: user.nickname,
      isLogin: true,
    })
  );

  alert("로그인 성공!");
  router.push("/app/dashboard");
};

/* 이동 함수 */
const goSignup = () => router.push("/signup");
const goWelcome = () => router.push("/welcome");
</script>

<style scoped>
/* 기존 디자인 그대로 */
.auth-page {
  width: 100%;
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  justify-content: center;
  align-items: center;
}
.auth-card {
  width: 420px;
  background: white;
  padding: 36px 40px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
}
.auth-card.small {
  width: 380px;
}
.title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 4px;
}
.subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 24px;
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
}
.input-row {
  position: relative;
  display: flex;
  align-items: center;
}
.primary-btn {
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
  cursor: pointer;
  font-weight: 600;
}
.icon-btn {
  position: absolute;
  right: 10px;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
}

.eye-icon {
  width: 20px;
  height: 20px;
}
.auth-logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  display: block;
}

</style>
