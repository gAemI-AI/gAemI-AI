<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <img src="@/assets/logo/gaemi.png" class="auth-logo" />
      <h1 class="title">회원가입</h1>

      <!-- ========================= -->
      <!--   1. 기본 정보 카드       -->
      <!-- ========================= -->
      <section class="section-card">
        <h2 class="card-title">기본 정보</h2>

        <div class="info-grid">

          <!-- 아이디 -->
          <div class="field">
            <label>아이디</label>
            <div class="input-row">
              <input v-model="form.username" type="text" placeholder="아이디" />
              <button class="tiny-btn" @click="checkUsername">중복 확인</button>
            </div>
            <p v-if="usernameStatus === 'ok'" class="success-msg">✔ 사용 가능한 아이디입니다.</p>
            <p v-if="usernameStatus === 'exists'" class="error-msg">❌ 이미 존재하는 아이디입니다.</p>
          </div>

          <!-- 닉네임 -->
          <div class="field">
            <label>닉네임</label>
            <div class="input-row">
              <input v-model="form.nickname" type="text" placeholder="닉네임" />
              <button class="tiny-btn" @click="checkNickname">중복 확인</button>
            </div>
            <p v-if="nicknameStatus === 'ok'" class="success-msg">✔ 사용 가능한 닉네임입니다.</p>
            <p v-if="nicknameStatus === 'exists'" class="error-msg">❌ 이미 존재하는 닉네임입니다.</p>
          </div>

          <!-- 비밀번호 -->
          <div class="field">
            <label>비밀번호</label>
            <div class="input-row">
              <input
                :type="showPw1 ? 'text' : 'password'"
                v-model="form.password"
                placeholder="비밀번호 (문자+숫자 8자 이상)"
              />
              <button class="icon-btn" @click="showPw1 = !showPw1">
                <img :src="showPw1 ? eyeClosed : eyeOpen" class="eye-icon" />
              </button>
            </div>

            <p v-if="passwordStatus === 'invalid'" class="error-msg">
              ❌ 비밀번호는 문자와 숫자를 포함한 8자 이상이어야 합니다.
            </p>

            <p v-else-if="passwordStatus === 'common'" class="error-msg">
              ⚠ 너무 흔한 비밀번호입니다.
            </p>
          </div>

          <!-- 비밀번호 확인 -->
          <div class="field">
            <label>비밀번호 확인</label>
            <div class="input-row">
              <input
                :type="showPw2 ? 'text' : 'password'"
                v-model="form.passwordConfirm"
                placeholder="비밀번호 확인"
              />
              <button class="icon-btn" @click="showPw2 = !showPw2">
                <img :src="showPw2 ? eyeClosed : eyeOpen" class="eye-icon" />
              </button>
            </div>

            <p v-if="passwordMatchStatus === 'mismatch'" class="error-msg">❌ 비밀번호가 일치하지 않습니다.</p>
            <p v-if="passwordMatchStatus === 'match'" class="success-msg">✔ 비밀번호가 일치합니다.</p>
          </div>

          <!-- 이메일 -->
          <div class="field">
            <label>이메일</label>
            <input
              v-model="form.email"
              class="input"
              placeholder="example@email.com"
              @input="validateEmail"
            />
            <p v-if="emailStatus === 'invalid'" class="error-msg">❌ 유효하지 않은 이메일 형식입니다.</p>
            <p v-if="emailStatus === 'valid'" class="success-msg">✔ 사용 가능한 이메일입니다.</p>
          </div>

          <!-- 전화번호 -->
          <!-- <div class="field">
            <label>전화번호</label>
            <input
              v-model="form.phone"
              class="input"
              placeholder="01012345678"
              @input="handlePhoneInput"
            />
            <p v-if="phoneStatus === 'invalid'" class="error-msg">❌ 전화번호는 숫자만 입력할 수 있습니다.</p>
          </div> -->

        </div> <!-- info-grid -->
      </section>

      <!-- ========================= -->
      <!--   2. 관심 종목 카드       -->
      <!-- ========================= -->
      <section class="section-card">
        <h2 class="card-title">관심 종목 설정</h2>
        <p class="subtitle">
          자주 확인할 종목을 미리 등록해두면 대시보드에서 더 빠르게 볼 수 있어요.
        </p>

        <input
          type="text"
          class="input"
          v-model="searchQuery"
          placeholder="종목명 또는 코드 검색"
        />

        <div v-if="filteredStocks.length > 0" class="search-results">
          <div class="stock-item" v-for="stock in filteredStocks" :key="stock.code">
            <span>{{ stock.name }} ({{ stock.code }})</span>
            <span
              class="star"
              :class="{ active: isFavorite(stock.code) }"
              @click="toggleFavorite(stock.code)"
            >★</span>
          </div>
        </div>

        <div v-if="form.favorites.length > 0" class="selected-favorites">
          <h4 class="fav-title">선택된 종목 목록</h4>
          <ul>
            <li v-for="code in form.favorites" :key="code">
              {{ getStockName(code) }} ({{ code }})
              <span class="star active">★</span>
            </li>
          </ul>
        </div>
      </section>

      <button class="primary-btn" @click="onSubmit">가입하기</button>

      <p class="footer-text">
        이미 계정이 있으신가요?
        <span class="link" @click="goLogin">로그인</span> |
        <span class="link" @click="goWelcome">메인으로</span>
      </p>

    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { STOCK_LIST } from "@/data/stocks.js";
import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";

const hangulToEngMap = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t','ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g','ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m'
};

function convertHangulToEng(input) {
  return input.split("").map(ch => hangulToEngMap[ch] || ch).join("");
}

const router = useRouter();

const form = ref({
  username: "",
  nickname: "",
  password: "",
  passwordConfirm: "",
  email: "",
  // phone: "",
  favorites: []
});

/* validation, watch, toggle, submit — 전체 그대로 유지 */
const usernameStatus = ref(null);
const nicknameStatus = ref(null);

const checkUsername = () => {
  const username = form.value.username.trim();
  if (!username) return;

  usernameStatus.value = "ok";
};

const checkNickname = () => {
  const nickname = form.value.nickname.trim();
  if (!nickname) return;

  nicknameStatus.value = "ok";
};


/* 비밀번호 + 일치 검증 */
const passwordStatus = ref(null);
const passwordMessage = ref("");
const passwordMatchStatus = ref(null);

const isValidPassword = (pw) => {
  if (!pw || pw.length < 8) return false;
  return /[A-Za-z]/.test(pw) && /[0-9]/.test(pw);
};

watch(
  () => form.value.password,
  (val) => {
    const converted = convertHangulToEng(val || "");
    if (converted !== val) {
      form.value.password = converted;
      return;
    }
    if (!converted) {
      passwordStatus.value = null;
      passwordMatchStatus.value = null;
      return;
    }
    passwordStatus.value = isValidPassword(converted) ? "valid" : "invalid";
    if (form.value.passwordConfirm) {
      passwordMatchStatus.value =
        form.value.passwordConfirm === converted ? "match" : "mismatch";
    }
  }
);

watch(
  () => form.value.passwordConfirm,
  (val) => {
    const converted = convertHangulToEng(val || "");
    if (converted !== val) {
      form.value.passwordConfirm = converted;
      return;
    }
    if (!converted) {
      passwordMatchStatus.value = null;
      return;
    }
    passwordMatchStatus.value =
      converted === form.value.password ? "match" : "mismatch";
  }
);

/* 이메일 */
const emailStatus = ref(null);
const validateEmail = () => {
  const email = form.value.email;
  if (!email) return (emailStatus.value = null);
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  emailStatus.value = emailRegex.test(email) ? "valid" : "invalid";
};

/* 전화번호 */
// const phoneStatus = ref(null);
// const handlePhoneInput = (e) => {
//   const onlyNumbers = e.target.value.replace(/[^0-9]/g, "");
//   phoneStatus.value = onlyNumbers !== e.target.value ? "invalid" : null;
//   form.value.phone = onlyNumbers;
// };

/* 관심 종목 */
const searchQuery = ref("");
const filteredStocks = computed(() =>
  !searchQuery.value.trim()
    ? []
    : STOCK_LIST.filter(
        (s) =>
          s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          s.code.includes(searchQuery.value)
      )
);

const toggleFavorite = (code) => {
  const i = form.value.favorites.indexOf(code);
  i === -1 ? form.value.favorites.push(code) : form.value.favorites.splice(i, 1);
};

const isFavorite = (code) => form.value.favorites.includes(code);
const getStockName = (code) =>
  STOCK_LIST.find((s) => s.code === code)?.name || "";

const onSubmit = async () => {
  // 🔧 1. 서버 요청 전 상태 초기화
  usernameStatus.value = "";
  nicknameStatus.value = "";

  try {
    const res = await axios.post("/api/v1/users/register/", {
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      password_confirm: form.value.passwordConfirm,
      nickname: form.value.nickname,
    });

    alert("회원가입이 완료되었습니다.");
    router.push("/login");

  } catch (err) {
    const data = err?.response?.data;

    // 🔧 2. 서버 기준 중복 처리
    if (data?.username) {
      usernameStatus.value = "exists";
    }
    if (data?.nickname) {
      nicknameStatus.value = "exists";
    }
    if (data?.error?.[0]?.includes("too common")) {
      passwordStatus.value = "common";
      passwordMessage.value = "너무 흔한 비밀번호입니다.";
      return;
    }

    alert(
      data?.messagee ||
      "회원가입에 실패했습니다. 아이디 또는 닉네임을 확인해주세요.");
  }
};

const showPw1 = ref(false);
const showPw2 = ref(false);

const goLogin = () => router.push("/login");
const goWelcome = () => router.push("/welcome");
</script>

<style scoped>
/* ======================= */
/*        Layout           */
/* ======================= */
.auth-wrapper {
  width: 100%;
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.auth-card {
  background: white;
  width: 800px; /* 확장됨 */
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
}

/* ======================= */
/*     Card Sections       */
/* ======================= */
.section-card {
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 14px;
}

.subtitle {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 12px;
}

/* ======================= */
/*       2-Column Grid     */
/* ======================= */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-row {
  position: relative;
  display: flex;
  gap: 8px;
  align-items: center;
}

.input,
input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.tiny-btn {
  padding: 8px 12px;
  background: #2563eb;
  min-width: 80px;
  text-align: center;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
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

/* ======================= */
/*       Messages          */
/* ======================= */
.success-msg {
  color: #2563eb;
  font-size: 12px;
}

.error-msg {
  color: #dc2626;
  font-size: 12px;
}

/* ======================= */
/*   관심 종목 List        */
/* ======================= */
.search-results {
  margin-top: 12px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  background: #f3f4f6;
  padding: 10px;
  border-radius: 8px;
  margin-top: 6px;
}

.star {
  cursor: pointer;
  font-size: 18px;
  color: #d1d5db;
}

.star.active {
  color: #2563eb;
}

.selected-favorites {
  margin-top: 16px;
  background: #f3f4f6;
  padding: 12px;
  border-radius: 8px;
}

.fav-title {
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 14px;
}

.selected-favorites li {
  margin-bottom: 6px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ======================= */
/*        Buttons          */
/* ======================= */
.primary-btn {
  width: 100%;
  padding: 14px;
  margin-top: 24px;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  color: white;
  cursor: pointer;
}

.footer-text {
  margin-top: 20px;
  text-align: center;
}

.link {
  color: #2563eb;
  cursor: pointer;
  font-weight: bold;
}
.auth-logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  display: block;
}
/* 🔧 input 깨짐 방지 핵심 패치 */
.input-row input,
.input {
  min-width: 0;
  box-sizing: border-box;
}

</style>
