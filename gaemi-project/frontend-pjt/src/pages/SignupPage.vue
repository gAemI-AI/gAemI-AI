<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="logo-wrapper">
        <img src="@/assets/logo/gaemi.png" class="auth-logo" />
      </div>
      <h1 class="title">회원가입</h1>
      <p class="page-subtitle">계정을 만들고 투자를 시작해보세요</p>

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
            <p v-if="passwordStatus === 'valid'" class="success-msg">
              ✔ 사용 가능한 비밀번호입니다.
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

      <div class="footer-area">
        <p class="footer-text">
          이미 계정이 있으신가요? <span class="link" @click="goLogin">로그인</span>
        </p>
        <p class="footer-secondary">
          <span class="link" @click="goWelcome">메인으로 돌아가기</span>
        </p>
      </div>

    </div>

    <!-- 회원가입 성공 팝업 -->
    <transition name="modal-fade">
      <div v-if="showSuccessModal" class="modal-overlay">
        <div class="success-modal">
          <div class="modal-icon">✓</div>
          <h2 class="modal-title">회원가입 성공!</h2>
          <p class="modal-subtitle">{{ form.username }}님, 환영합니다</p>
          <p class="modal-loading">잠시만 기다려주세요...</p>
          <div class="spinner"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
/* 기존 script 코드 그대로 — 수정 없음 */
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { STOCK_LIST } from "@/data/stocks.js";
import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";

const router = useRouter();
const showSuccessModal = ref(false);

const hangulToEngMap = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t','ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g','ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m'
};

function convertHangulToEng(input) {
  return input.split("").map(ch => hangulToEngMap[ch] || ch).join("");
}

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
const EXIST_USERNAMES = ["admin", "test", "gaemi"];
const EXIST_NICKNAMES = ["철수", "영희", "주연"];

const checkUsername = () => {
  if (!form.value.username.trim()) return;
  usernameStatus.value = EXIST_USERNAMES.includes(form.value.username)
    ? "exists" : "ok";
};

const checkNickname = () => {
  if (!form.value.nickname.trim()) return;
  nicknameStatus.value = EXIST_NICKNAMES.includes(form.value.nickname)
    ? "exists" : "ok";
};

/* 비밀번호 + 일치 검증 */
const passwordStatus = ref(null);
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
  if (usernameStatus.value !== "ok") return alert("아이디 중복 확인을 완료해주세요.");
  if (nicknameStatus.value !== "ok") return alert("닉네임 중복 확인을 완료해주세요.");

  const pw = form.value.password;
  const pwRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
  if (!pwRegex.test(pw)) return alert("비밀번호는 문자+숫자 포함 8자 이상이어야 합니다.");

  if (form.value.password !== form.value.passwordConfirm)
    return alert("비밀번호 확인이 일치하지 않습니다.");

  if (emailStatus.value !== "valid")
    return alert("올바른 이메일을 입력해주세요.");

  try {
    // 백엔드 API에 회원가입 요청
    const response = await fetch("http://localhost:8000/api/v1/users/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: form.value.username,
        password: form.value.password,
        password_confirm: form.value.passwordConfirm,
        nickname: form.value.nickname,
        email: form.value.email,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const user = data.user;
    
    // 회원가입 성공 시 자동 로그인 처리
    // ⭐ favorites는 저장하지 않음 (API로만 관리)
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
    
    // JWT 토큰 저장
    localStorage.setItem("accessToken", data.access);
    localStorage.setItem("refreshToken", data.refresh);
    
    // 관심 종목 추가 (선택적)
    if (form.value.favorites.length > 0) {
      const accessToken = data.access;
      try {
        for (const stockCode of form.value.favorites) {
          await fetch("http://localhost:8000/api/v1/watchlist/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
              stock: stockCode,
            }),
          });
        }
      } catch (watchlistError) {
        console.warn("관심 종목 추가 중 오류:", watchlistError);
        // 관심 종목 추가 실패는 회원가입 성공을 방해하지 않음
      }
    }
    
    // 성공 팝업 표시
    showSuccessModal.value = true;

    // 2초 후 대시보드로 이동
    setTimeout(() => {
      router.push("/app/dashboard");
    }, 2000);
  } catch (error) {
    console.error("회원가입 오류:", error);
    alert(error.message || "회원가입 중 오류가 발생했습니다. 다시 시도해주세요.");
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
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.auth-card {
  background: white;
  width: 100%;
  max-width: 720px;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

/* 로고 래퍼 */
.logo-wrapper {
  margin-bottom: 24px;
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

/* 타이틀 */
.title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #111827;
  letter-spacing: -0.5px;
}

.page-subtitle {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 32px 0;
  font-weight: 400;
}

/* ======================= */
/*     Card Sections       */
/* ======================= */
.section-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 14px 0;
  color: #111827;
  letter-spacing: -0.3px;
}

.subtitle {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 16px 0;
  font-weight: 400;
}

/* ======================= */
/*       2-Column Grid     */
/* ======================= */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 24px;
}

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

.input-row {
  position: relative;
  display: flex;
  gap: 10px;
  align-items: center;
}

.input,
input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.input:focus,
input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input::placeholder,
input::placeholder {
  color: #9ca3af;
}

/* 중복 확인 버튼 */
.tiny-btn {
  padding: 10px 14px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  min-width: 90px;
  text-align: center;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tiny-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* 아이콘 버튼 */
.icon-btn {
  position: absolute;
  right: 12px;
  border: none;
  background: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s ease;
}

.icon-btn:hover {
  opacity: 0.7;
}

.eye-icon {
  width: 20px;
  height: 20px;
}

/* ======================= */
/*       Messages          */
/* ======================= */
.success-msg {
  color: #059669;
  font-size: 12px;
  margin: 0;
  font-weight: 500;
}

.error-msg {
  color: #dc2626;
  font-size: 12px;
  margin: 0;
  font-weight: 500;
}

/* ======================= */
/*   관심 종목 검색 & List */
/* ======================= */
.search-results {
  margin-top: 12px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s ease;
}

.stock-item:hover {
  background: #f9fafb;
}

.stock-item:last-child {
  border-bottom: none;
}

.star {
  cursor: pointer;
  font-size: 20px;
  color: #d1d5db;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.star:hover {
  color: #fbbf24;
}

.star.active {
  color: #2563eb;
}

.selected-favorites {
  margin-top: 16px;
  background: #f9fafb;
  padding: 16px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.fav-title {
  margin: 0 0 12px 0;
  font-weight: 600;
  font-size: 13px;
  color: #111827;
}

.selected-favorites ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.selected-favorites li {
  margin-bottom: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #374151;
}

.selected-favorites li:last-child {
  margin-bottom: 0;
}

/* ======================= */
/*        Buttons          */
/* ======================= */
.primary-btn {
  width: 100%;
  padding: 14px 0;
  margin-top: 32px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  color: white;
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
/*        Footer           */
/* ======================= */
.footer-area {
  text-align: center;
  margin-top: 28px;
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
  cursor: pointer;
  font-weight: 600;
  transition: color 0.2s ease;
}

.link:hover {
  color: #1d4ed8;
}

/* ======================= */
/*      Responsive         */
/* ======================= */
@media (max-width: 640px) {
  .auth-card {
    padding: 32px 24px;
  }

  .title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .section-card {
    padding: 20px;
  }

  .card-title {
    font-size: 15px;
  }

  .subtitle {
    font-size: 12px;
  }
}

/* 핵심 input 패치 */
.input-row input,
.input {
  min-width: 0;
  box-sizing: border-box;
}

/* ======================= */
/*    성공 모달 팝업        */
/* ======================= */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 48px;
  color: white;
  font-weight: 700;
  animation: iconScale 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes iconScale {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.modal-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #111827;
  letter-spacing: -0.5px;
}

.modal-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 20px 0;
  font-weight: 400;
}

.modal-loading {
  font-size: 14px;
  color: #9ca3af;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 모달 페이드 트랜지션 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
