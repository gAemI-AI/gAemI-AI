<!-- src/pages/WelcomePage.vue -->
<template>
  <div class="welcome-page">
    <div class="content-area">
      <main class="hero-section">
        <!-- 로고 -->
        <img src="@/assets/logo/gaemi.png" class="hero-logo" />
        <h1 class="hero-title">시간 없는 개미를 위한 AI 투자 파트너</h1>
        <p class="hero-desc">
          주가는 gAemI가 보고, 판단은 당신이 합니다
        </p>
        <br></br>

        <div class="hero-actions">
          <button class="primary-btn" @click="goSignup">처음이신가요?</button>
          <button class="ghost-btn" @click="goLogin">로그인</button>
        </div>

        <section class="features">
          <div class="feature-item">
            <div class="emoji">📊</div>
            <h3>실시간 주가</h3>
            <p>관심 종목의 가격을 실시간으로 확인하세요</p>
          </div>
          <div class="feature-item">
            <div class="emoji">🤖</div>
            <h3>AI 뉴스 분석</h3>
            <p>중요한 뉴스를 AI가 분석해드립니다</p>
          </div>
          <div class="feature-item">
            <div class="emoji">🔔</div>
            <h3>실시간 알림</h3>
            <p>가격 변동과 뉴스를 놓치지 마세요</p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goSignup = () => router.push('/signup')
const goLogin = () => router.push('/login')
</script>

<style scoped>
/* 바깥 흰 배경 */
.welcome-page {
  min-height: 100vh;
  background: #f5f6fa;
  display: flex;
  justify-content: center;
}

/* 대시보드 중앙 회색 박스와 동일한 폭/배경 */
.content-area {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  padding: 40px 40px;
  box-sizing: border-box;
}

/* 상단 간단 헤더 */
.top-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 80px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.top-login-btn {
  border: none;
  background: transparent;
  font-size: 14px;
  cursor: pointer;
  color: #2563eb;
}

/* 중앙 히어로 영역 */
.hero-section {
  text-align: center;
}

.hero-subtitle {
  font-size: 16px;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 8px;
}

.hero-title {
  font-size: 24px;
  line-height: 1.6;
  font-weight: 600;
  margin-bottom: 32px;
}

/* 버튼 영역 */
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 60px;
}

.primary-btn {
  min-width: 160px;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  background: #2563eb;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
}

.primary-btn:hover {
  background: #1d4ed8;
}

.ghost-btn {
  min-width: 120px;
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #111827;
  font-weight: 500;
  cursor: pointer;
}

.ghost-btn:hover {
  background: #f9fafb;
}

/* 하단 기능 소개 카드 */
.features {
  display: flex;
  justify-content: center;
  gap: 60px;
  margin-top: 40px;
}

.feature-item {
  width: 200px;
}

.emoji {
  font-size: 40px;
  margin-bottom: 12px;
}

.feature-item h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.feature-item p {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.hero-desc {
  font-size: 14px;
  color: gray;
}
.hero-logo {
  width: 72px;
  height: 72px;
  margin-bottom: 16px;
}

</style>
