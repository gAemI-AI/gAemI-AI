<!-- src/pages/WelcomePage.vue -->
<template>
  <div class="welcome-page">
    <div class="content-area">
      <main class="hero-section">
        <!-- 로고 -->
        <div class="logo-wrapper">
          <img src="@/assets/logo/gaemi.png" class="hero-logo" />
        </div>

        <!-- 메인 타이틀 -->
        <h1 class="hero-title">AI 투자 파트너<br><span class="highlight">gAemI</span></h1>
        <p class="hero-desc">
          똑똑한 분석, 당신의 결정
        </p>

        <!-- CTA 버튼 -->
        <div class="hero-actions">
          <button class="primary-btn" @click="goSignup">시작하기</button>
          <button class="secondary-btn" @click="goLogin">로그인</button>
        </div>

        <!-- 특징 섹션 -->
        <section class="features">
          <div class="feature-card">
            <div class="feature-icon-wrapper">
              <span class="feature-icon">📊</span>
            </div>
            <h3>실시간 주가 분석</h3>
            <p>관심 종목의 움직임을<br>한눈에 파악하세요</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper">
              <span class="feature-icon">🤖</span>
            </div>
            <h3>AI 뉴스 분석</h3>
            <p>시장에 영향을 주는<br>뉴스를 먼저 만나세요</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper">
              <span class="feature-icon">🔔</span>
            </div>
            <h3>똑똑한 알림</h3>
            <p>중요한 변화를 놓치지 않고<br>받아보세요</p>
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
/* 페이지 전체 배경 */
.welcome-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 컨텐츠 영역 */
.content-area {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  padding: 60px 40px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

/* 히어로 섹션 */
.hero-section {
  text-align: center;
  width: 100%;
}

/* 로고 래퍼 */
.logo-wrapper {
  margin-bottom: 32px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.hero-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

/* 메인 타이틀 */
.hero-title {
  font-size: 48px;
  line-height: 1.2;
  font-weight: 700;
  margin: 0 0 20px 0;
  color: #111827;
  letter-spacing: -0.5px;
}

.hero-title .highlight {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 서브 설명 */
.hero-desc {
  font-size: 18px;
  color: #6b7280;
  margin: 0 0 48px 0;
  font-weight: 400;
  letter-spacing: -0.3px;
}

/* 버튼 영역 */
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 80px;
}

/* 주 CTA 버튼 */
.primary-btn {
  min-width: 180px;
  padding: 16px 32px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
}

.primary-btn:active {
  transform: translateY(0);
}

/* 보조 버튼 */
.secondary-btn {
  min-width: 140px;
  padding: 16px 32px;
  border-radius: 12px;
  border: 1.5px solid #e5e7eb;
  background: #ffffff;
  color: #111827;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.secondary-btn:hover {
  border-color: #d1d5db;
  background: #f9fafb;
  transform: translateY(-2px);
}

.secondary-btn:active {
  transform: translateY(0);
}

/* 특징 섹션 */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 60px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

/* 특징 카드 */
.feature-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: #e5e7eb;
}

/* 아이콘 래퍼 */
.feature-icon-wrapper {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #f0f4ff 0%, #f5f8ff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon {
  font-size: 32px;
}

/* 카드 제목 */
.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #111827;
  letter-spacing: -0.3px;
}

/* 카드 설명 */
.feature-card p {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
  letter-spacing: -0.2px;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .content-area {
    padding: 40px 24px;
    min-height: auto;
  }

  .hero-title {
    font-size: 36px;
    margin-bottom: 16px;
  }

  .hero-desc {
    font-size: 16px;
    margin-bottom: 32px;
  }

  .hero-actions {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 60px;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
    min-width: unset;
  }

  .features {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-top: 40px;
  }

  .logo-wrapper {
    margin-bottom: 24px;
  }

  .hero-logo {
    width: 72px;
    height: 72px;
  }

  .feature-card {
    padding: 24px 20px;
  }

  .feature-icon-wrapper {
    width: 56px;
    height: 56px;
  }

  .feature-icon {
    font-size: 28px;
  }

  .feature-card h3 {
    font-size: 16px;
  }

  .feature-card p {
    font-size: 13px;
  }
}

/* 다크 모드 대비 (선택사항) */
@media (prefers-color-scheme: dark) {
  .welcome-page {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  }

  .hero-title {
    color: #f9fafb;
  }

  .hero-desc {
    color: #9ca3af;
  }

  .feature-card {
    background: #2d3748;
    border-color: #374151;
  }

  .feature-icon-wrapper {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  }

  .feature-card h3 {
    color: #f9fafb;
  }

  .feature-card p {
    color: #9ca3af;
  }

  .secondary-btn {
    background: #2d3748;
    color: #f9fafb;
    border-color: #374151;
  }

  .secondary-btn:hover {
    background: #374151;
    border-color: #4b5563;
  }
}
</style>
