<template>
  <div class="login-root">
    <!-- 🔹 대시보드의 회색 박스(.main-content)와 동일한 폭 -->
    <div class="login-shell">
      <div class="login-card">
        <!-- 로고 -->
        <img src="@/assets/logo/gaemi.png" class="logo" alt="gAemI Logo" />

        <h2 class="title">gAemI 로그인</h2>
        <p class="subtitle">소셜 계정으로 빠르게 로그인하세요</p>

        <!-- 소셜 로그인 버튼 가로 배치 -->
        <div class="social-row">
          <button class="social-btn google" @click="login('google')">
            <!-- 아이콘은 네가 쓰던 방식 그대로 써도 됨 (텍스트/이미지 자유) -->
            <span class="icon">G</span>
            Google 로그인
          </button>

          <button class="social-btn github" @click="login('github')">
            <span class="icon">🐙</span>
            GitHub 로그인
          </button>

          <button class="social-btn kakao" @click="login('kakao')">
            <span class="icon">K</span>
            Kakao 로그인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
function login(provider) {
  // 백엔드 OAuth (지금 404 나는 건 정상)
  window.location.href = `http://localhost:8000/api/auth/social/${provider}/login/`;
}
</script>

<style scoped>
/* 전체 배경 (레이아웃이 없는 페이지라서 여기서 배경 처리) */
.login-root {
  min-height: 100vh;
  background: #f5f6fa;
}

/* 🔹 대시보드의 .main-content와 똑같은 크기/정렬 */
.login-shell {
  width: 100%;
  max-width: 1400px;     /* 👉 MainLayout.vue 의 .main-content 와 동일 */
  margin: 0 auto;
  padding: 20px 40px;

  display: flex;
  align-items: center;
  justify-content: center;

  min-height: 100vh;     /* 세로 중앙 정렬 */
}

/* 로그인 카드 */
.login-card {
  width: 100%;
  max-width: 700px;
  background: #ffffff;
  padding: 40px 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  text-align: center;
}

/* 로고 */
.logo {
  width: 72px;
  height: 72px;
  margin-bottom: 16px;
}

/* 텍스트 */
.title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 32px;
}

/* 소셜 버튼 가로 배치 */
.social-row {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 공통 버튼 스타일 */
.social-btn {
  flex: 1;
  height: 48px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.1s;
}

.social-btn:hover {
  background: #f3f4f6;
}

/* 아이콘 자리 (텍스트/이미지 뭐든 넣어도 됨) */
.icon {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* 서비스별 색감 */
.google {
  border-color: #dadce0;
}

.github {
  border-color: #1f2937;
  background: #1f2937;
  color: white;
}

.github:hover {
  background: #374151;
}

.kakao {
  background: #fee500;
  border-color: #fee500;
}
</style>
