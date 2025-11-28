<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1 class="title">회원가입</h1>
      <p class="subtitle">새로운 계정을 만드세요</p>

      <!-- 기본 정보 -->
      <section class="section">
        <h2 class="section-title">기본 정보</h2>

        <div class="form-grid">
          <!-- 아이디 -->
          <div class="field">
            <label>아이디</label>
            <div class="input-row">
              <input v-model="form.username" type="text" placeholder="아이디" />
              <button class="tiny-btn" @click="checkUsername">중복 확인</button>
            </div>

            <p v-if="usernameStatus === 'ok'" class="success-msg">✔ 사용 가능한 아이디입니다.</p>
            <p v-if="usernameStatus === 'exists'" class="error-msg">❌ 사용 불가능한 아이디입니다.</p>
          </div>

          <!-- 닉네임 -->
          <div class="field">
            <label>닉네임</label>
            <div class="input-row">
              <input v-model="form.nickname" type="text" placeholder="닉네임" />
              <button class="tiny-btn" @click="checkNickname">중복 확인</button>
            </div>

            <p v-if="nicknameStatus === 'ok'" class="success-msg">✔ 사용 가능한 닉네임입니다.</p>
            <p v-if="nicknameStatus === 'exists'" class="error-msg">❌ 사용 불가능한 닉네임입니다.</p>
          </div>

          <!-- 비밀번호 -->
          <div class="field">
            <label>비밀번호</label>
            <div class="input-row">
              <input
                :type="showPw1 ? 'text' : 'password'"
                v-model="form.password"
                placeholder="비밀번호 (최소 6글자)"
              />
              <button class="ghost-btn" @click="showPw1 = !showPw1">보기</button>
            </div>
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
              <button class="ghost-btn" @click="showPw2 = !showPw2">보기</button>
            </div>
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

      <!-- 🔥 관심 종목 선택 기능 -->
      <section class="section">
        <h2 class="section-title">관심 종목 선택</h2>

        <!-- 검색창 -->
        <input
          type="text"
          class="input"
          v-model="searchQuery"
          placeholder="종목명 또는 코드 검색"
        />

        <!-- 검색 결과 -->
        <div v-if="filteredStocks.length > 0" class="search-results">
          <div
            class="stock-item"
            v-for="stock in filteredStocks"
            :key="stock.code"
          >
            <span>{{ stock.name }} ({{ stock.code }})</span>

            <span
              class="star"
              :class="{ active: isFavorite(stock.code) }"
              @click="toggleFavorite(stock.code)"
            >
              ⭐
            </span>
          </div>
        </div>

        <!-- 선택된 종목 목록 -->
        <div v-if="form.favorites.length > 0" class="selected-favorites">
          <h4>선택된 종목 목록</h4>
          <ul>
            <li v-for="code in form.favorites" :key="code">
              ⭐ {{ getStockName(code) }} ({{ code }})
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
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { STOCK_LIST } from "@/data/stocks.js";

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
  favorites: [] // ⭐ 관심종목 저장
});

/* 관심 종목 검색 */
const searchQuery = ref("");

const filteredStocks = computed(() => {
  if (!searchQuery.value.trim()) return [];
  const q = searchQuery.value.toLowerCase();
  return STOCK_LIST.filter(
    (s) => s.name.toLowerCase().includes(q) || s.code.includes(q)
  );
});

/* 관심 종목 추가/삭제 */
const toggleFavorite = (code) => {
  const index = form.value.favorites.indexOf(code);
  if (index === -1) form.value.favorites.push(code);
  else form.value.favorites.splice(index, 1);
};

const isFavorite = (code) => form.value.favorites.includes(code);

const getStockName = (code) =>
  STOCK_LIST.find((s) => s.code === code)?.name || "";

/* 중복 확인 */
const usernameStatus = ref(null);
const nicknameStatus = ref(null);
const EXIST_USERNAMES = ["admin", "test", "gaemi"];
const EXIST_NICKNAMES = ["철수", "영희", "주연"];

const checkUsername = () => {
  if (!form.value.username.trim()) return alert("아이디를 입력하세요.");
  usernameStatus.value = EXIST_USERNAMES.includes(form.value.username)
    ? "exists"
    : "ok";
};

const checkNickname = () => {
  if (!form.value.nickname.trim()) return alert("닉네임을 입력하세요.");
  nicknameStatus.value = EXIST_NICKNAMES.includes(form.value.nickname)
    ? "exists"
    : "ok";
};

/* 제출 */
const onSubmit = () => {
  if (usernameStatus.value !== "ok")
    return alert("아이디 중복 확인을 완료해주세요.");
  if (nicknameStatus.value !== "ok")
    return alert("닉네임 중복 확인을 완료해주세요.");
  if (form.value.password !== form.value.passwordConfirm)
    return alert("비밀번호가 일치하지 않습니다.");

  // ⭐ 관심 종목 포함 전체 유저 데이터 저장
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
/* 전체 정렬 */
.auth-wrapper {
  width: 100%;
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

/* 카드 */
.auth-card {
  background: white;
  width: 460px;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.title {
  font-size: 24px;
  font-weight: 700;
}
.subtitle {
  margin-top: -4px;
  color: #6b7280;
}

/* 섹션 */
.section {
  margin-top: 28px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* 폼 */
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
  gap: 8px;
}

.input,
input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

/* 스위치 버튼 */
.switch-group {
  display: flex;
  gap: 10px;
}
.switch-btn {
  padding: 6px 12px;
  border-radius: 6px;
  background: #e5e7eb;
  border: none;
  cursor: pointer;
}
.switch-btn.active {
  background: #2563eb;
  color: white;
}

/* 버튼 */
.primary-btn {
  margin-top: 24px;
  width: 100%;
  background: #2563eb;
  color: white;
  padding: 12px;
  border-radius: 8px;
  border: none;
  font-size: 15px;
  cursor: pointer;
}
.primary-btn:hover {
  background: #1d4ed8;
}

.tiny-btn {
  padding: 8px 10px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.ghost-btn {
  padding: 8px 10px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 메세지 */
.success-msg {
  color: #2563eb;
  font-size: 12px;
}
.error-msg {
  color: #dc2626;
  font-size: 12px;
}

/* 하단 링크 */
.footer-text {
  text-align: center;
  margin-top: 20px;
  color: #6b7280;
}
.link {
  color: #2563eb;
  cursor: pointer;
}
</style>
