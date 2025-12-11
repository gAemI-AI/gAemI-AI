<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1 class="title">회원가입</h1>
      <br></br>
      <!-- 기본 정보 -->
      <section class="section">

        <div class="form-grid">
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
                placeholder="비밀번호 (문자+숫자 6자 이상)"
              />
              <button class="icon-btn" @click="showPw1 = !showPw1">
                <img :src="showPw1 ? eyeClosed : eyeOpen" class="eye-icon" />
              </button>
            </div>

            <p v-if="passwordStatus === 'invalid'" class="error-msg">
              ❌ 비밀번호는 문자와 숫자를 포함한 6자 이상이어야 합니다.
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

            <p v-if="passwordMatchStatus === 'mismatch'" class="error-msg">
              ❌ 비밀번호가 서로 일치하지 않습니다.
            </p>
            <p v-if="passwordMatchStatus === 'match'" class="success-msg">
              ✔ 비밀번호가 일치합니다.
            </p>
          </div>

          <!-- 연락처 -->
          <div class="field full">
            <label>연락처</label>
            <div class="switch-group">
              <button
                class="switch-btn"
                :class="{ active: form.contactType === 'email' }"
                @click="form.contactType = 'email'"
              >
                이메일
              </button>
              <button
                class="switch-btn"
                :class="{ active: form.contactType === 'phone' }"
                @click="form.contactType = 'phone'"
              >
                전화번호
              </button>
            </div>

            <input
              v-if="form.contactType === 'email'"
              v-model="form.email"
              class="input"
              placeholder="example@email.com"
            />
            <input
              v-if="form.contactType === 'phone'"
              v-model="form.phone"
              class="input"
              placeholder="010-0000-0000"
            />
          </div>
        </div>
      </section>

      <!-- 관심 종목 선택 -->
      <section class="section">
        <h2 class="section-title">관심 종목 선택</h2>

        <input
          type="text"
          class="input"
          v-model="searchQuery"
          placeholder="종목명 또는 코드 검색"
        />

        <!-- 검색 결과 -->
        <div v-if="filteredStocks.length > 0" class="search-results">
          <div class="stock-item" v-for="stock in filteredStocks" :key="stock.code">
            <span>{{ stock.name }} ({{ stock.code }})</span>
            <span
              class="star"
              :class="{ active: isFavorite(stock.code) }"
              @click="toggleFavorite(stock.code)"
            >
              ★
            </span>
          </div>
        </div>

        <!-- 선택된 종목 목록 -->
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
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { STOCK_LIST } from "@/data/stocks.js";
import eyeOpen from "@/assets/icons/eye-open.png";
import eyeClosed from "@/assets/icons/eye-closed.png";

/* 한글 자판 → 영문 자판 매핑 */
const hangulToEngMap = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t',
  'ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g',
  'ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b',
  'ㅜ':'n','ㅡ':'m'
};

/* 한글 입력을 강제로 영문으로 변환 */
function convertHangulToEng(input) {
  return input
    .split("")
    .map(ch => hangulToEngMap[ch] || ch)
    .join("");
}


const router = useRouter();

/* 폼 데이터 */
const form = ref({
  username: "",
  nickname: "",
  password: "",
  passwordConfirm: "",
  contactType: "email",
  email: "",
  phone: "",
  favorites: []
});

/* 아이디/닉네임 중복 확인 */
const usernameStatus = ref(null);
const nicknameStatus = ref(null);

const EXIST_USERNAMES = ["admin", "test", "gaemi"];
const EXIST_NICKNAMES = ["철수", "영희", "주연"];

const checkUsername = () => {
  if (!form.value.username.trim()) return;
  usernameStatus.value = EXIST_USERNAMES.includes(form.value.username)
    ? "exists"
    : "ok";
};

const checkNickname = () => {
  if (!form.value.nickname.trim()) return;
  nicknameStatus.value = EXIST_NICKNAMES.includes(form.value.nickname)
    ? "exists"
    : "ok";
};

/* 비밀번호 유효성 검사 */
const passwordStatus = ref(null);
const passwordMatchStatus = ref(null);

const isValidPassword = (pw) => {
  if (!pw || pw.length < 6) return false;
  const hasLetter = /[A-Za-z]/.test(pw);
  const hasNumber = /[0-9]/.test(pw);
  return hasLetter && hasNumber;
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
      return;
    }
    passwordStatus.value = isValidPassword(converted) ? "valid" : "invalid";
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
      passwordStatus.value = null;
      return;
    }
    passwordStatus.value = isValidPassword(converted) ? "valid" : "invalid";
  }
);

// watch(
//   () => form.value.password,
//   (pw) => {
//     if (!pw) {
//       passwordStatus.value = null;
//       return;
//     }
//     passwordStatus.value = isValidPassword(pw) ? "valid" : "invalid";
//   }
// );

// watch(
//   () => form.value.passwordConfirm,
//   (pwConfirm) => {
//     if (!pwConfirm) {
//       passwordMatchStatus.value = null;
//       return;
//     }
//     passwordMatchStatus.value =
//       pwConfirm === form.value.password ? "match" : "mismatch";
//   }
// );

/* 관심 종목 검색 */
const searchQuery = ref("");

const filteredStocks = computed(() => {
  if (!searchQuery.value.trim()) return [];
  const q = searchQuery.value.toLowerCase();
  return STOCK_LIST.filter(
    (s) => s.name.toLowerCase().includes(q) || s.code.includes(q)
  );
});

/* 관심 종목 관리 */
const toggleFavorite = (code) => {
  const index = form.value.favorites.indexOf(code);
  if (index === -1) form.value.favorites.push(code);
  else form.value.favorites.splice(index, 1);
};

const isFavorite = (code) => form.value.favorites.includes(code);

const getStockName = (code) =>
  STOCK_LIST.find((s) => s.code === code)?.name || "";

/* 제출 */
const onSubmit = () => {
  if (usernameStatus.value !== "ok") {
    alert("아이디 중복 확인을 완료해주세요.");
    return;
  }
  if (nicknameStatus.value !== "ok") {
    alert("닉네임 중복 확인을 완료해주세요.");
    return;
  }
    // 3️⃣ 비밀번호 형식 오류
    // 영문 + 숫자 + 최소 6글자
    const pw = form.value.password;
    const pwRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;

    if (!pwRegex.test(pw)) {
      alert("비밀번호는 문자와 숫자를 포함한 6자 이상이어야 합니다.");
      return;
    }

    // 4️⃣ 비밀번호 != 비밀번호 확인
    if (form.value.password !== form.value.passwordConfirm) {
      alert("비밀번호 확인이 일치하지 않습니다.");
      return;
    }

  localStorage.setItem("user", JSON.stringify(form.value));
  alert("회원가입 완료! 로그인 페이지로 이동합니다.");
  router.push("/login");
};

const showPw1 = ref(false);
const showPw2 = ref(false);

const goLogin = () => router.push("/login");
const goWelcome = () => router.push("/welcome");
</script>

<style scoped>
/* 기본 레이아웃 */
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
  width: 460px;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input,
input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.tiny-btn {
  white-space: nowrap;
  padding: 8px 12px;
  background: #2563eb;
  color: white;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
}

/* 아이콘 버튼 */
.icon-btn {
  border: none;
  background: none;
  cursor: pointer;
}

.eye-icon {
  width: 20px;
  height: 20px;
}

/* 메시지 */
.success-msg {
  color: #2563eb;
  font-size: 12px;
}

.error-msg {
  color: #dc2626;
  font-size: 12px;
}

/* 관심 종목 */
.stock-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f9fafb;
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

/* 선택된 관심 종목 목록 */
.selected-favorites {
  margin-top: 16px;
  background: #f9fafb;
  padding: 12px;
  border-radius: 8px;
}

.fav-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.selected-favorites li {
  padding-left: 0;
  font-size: 15px;
  margin-bottom: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 버튼 */
.primary-btn {
  width: 100%;
  margin-top: 24px;
  padding: 12px;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  border: none;
  font-size: 15px;
  cursor: pointer;
}

.footer-text {
  text-align: center;
  margin-top: 20px;
}

.link {
  color: #2563eb;
  cursor: pointer;
  font-weight: 500;
}
</style>
