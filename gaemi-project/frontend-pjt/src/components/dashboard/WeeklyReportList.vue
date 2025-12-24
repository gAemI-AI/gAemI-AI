<template>
  <div class="panel-box">
    <div class="panel-header">
      <h3 class="panel-title">주간 리포트</h3>
      <span v-if="reports.length > 0" class="badge">{{ reports.length }}</span>
    </div>

    <div v-if="isLoading" class="state-area">
      <div class="spinner"></div>
      <p>리포트 로딩 중...</p>
    </div>

    <div v-else-if="reports.length === 0" class="state-area">
      <p class="empty-text">발행된 리포트가 없습니다.</p>
    </div>

    <div v-else class="report-list">
      <div 
        v-for="report in reports" 
        :key="report.id" 
        class="report-card-wrapper"
      >
        <div 
          class="report-card" 
          :class="{ active: selectedReportId === report.id }"
          @click.stop="toggleReport(report.id)"
        >
          <div class="card-icon">📈</div>
          <div class="card-info">
            <span class="stock-name">{{ report.stock_name }}</span>
            <span class="report-date">
              {{ formatDate(report.start_date) }} ~ {{ formatDate(report.end_date) }}
            </span>
            <span class="weekly-return" :class="report.weekly_return >= 0 ? 'positive' : 'negative'">
              {{ report.weekly_return >= 0 ? '▲' : '▼' }} {{ Math.abs(report.weekly_return).toFixed(2) }}%
            </span>
          </div>
          <div class="arrow-indicator">{{ selectedReportId === report.id ? '▼' : '›' }}</div>
        </div>

        <transition name="expand">
          <div 
            v-if="selectedReportId === report.id" 
            class="report-detail"
            @click.stop
          >
            <div class="detail-section">
              <h4 class="section-title">📈 주간 실적</h4>
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">시작가</span>
                  <span class="stat-value">{{ report.start_price?.toLocaleString() }}원</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">종료가</span>
                  <span class="stat-value">{{ report.end_price?.toLocaleString() }}원</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">최고가</span>
                  <span class="stat-value">{{ report.weekly_high?.toLocaleString() }}원</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">최저가</span>
                  <span class="stat-value">{{ report.weekly_low?.toLocaleString() }}원</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4 class="section-title">💡 AI 분석 리포트</h4>
              <div class="markdown-content" v-html="renderMarkdown(report.summary_text)">
              </div>
            </div>

            <div class="detail-footer">
              <span class="created-at">
                작성일: {{ formatDateTime(report.created_at) }}
              </span>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { marked } from 'marked';
import { fetchWeeklyReports } from '@/api/reports';

const reports = ref([]);
const isLoading = ref(false);
const selectedReportId = ref(null);

// marked 설정
marked.setOptions({
  breaks: true,
  gfm: true,
});

const loadReports = async () => {
  isLoading.value = true;
  try {
    const data = await fetchWeeklyReports();
    console.log('Weekly Reports:', data);
    reports.value = data;
  } catch (e) {
    console.error("리포트 로드 실패:", e);
  } finally {
    isLoading.value = false;
  }
};

const toggleReport = (id) => {
  if (selectedReportId.value === id) {
    selectedReportId.value = null;
  } else {
    selectedReportId.value = id;
  }
};

const closePopup = () => {
  selectedReportId.value = null;
};

// 마크다운을 HTML로 렌더링
const renderMarkdown = (markdownText) => {
  if (!markdownText) return '<p>분석 내용이 없습니다.</p>';
  return marked(markdownText);
};

// 날짜 포맷 (YYYY-MM-DD -> MM월 DD일)
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr + 'T00:00:00');
  return `${date.getMonth() + 1}월 ${date.getDate()}일`;
};

// 날짜 시간 포맷 (YYYY-MM-DDTHH:MM:SS -> MM/DD HH:MM)
const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

onMounted(() => {
  loadReports();
  window.addEventListener('click', closePopup);
});

onUnmounted(() => {
  window.removeEventListener('click', closePopup);
});
</script>

<style scoped>
/* ✅ 박스 디자인 통일 */
.panel-box {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #191f28;
  margin: 0;
}

.badge {
  font-size: 11px;
  background: #3182f6;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-card-wrapper {
  position: relative;
}

/* 리포트 카드 */
.report-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #f9fafb;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.25s ease;
}

.report-card:hover {
  background: white;
  border-color: #3182f6;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.1);
}

.report-card.active {
  background: white;
  border-color: #3182f6;
  box-shadow: 0 4px 12px rgba(49, 130, 246, 0.15);
}

.card-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-name {
  font-size: 14px;
  font-weight: 600;
  color: #191f28;
}

.report-date {
  font-size: 12px;
  color: #8b95a1;
}

.weekly-return {
  font-size: 12px;
  font-weight: 600;
}

.weekly-return.positive {
  color: #ef4444;
}

.weekly-return.negative {
  color: #3b82f6;
}

.arrow-indicator {
  color: #d1d6db;
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.report-card.active .arrow-indicator {
  color: #3182f6;
}

/* 📋 상세 정보 패널 */
.report-detail {
  margin-top: 8px;
  background: #f0f4ff;
  border: 1px solid #c7d2e5;
  border-radius: 12px;
  padding: 16px;
  animation: slideDown 0.25s ease;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-of-type {
  margin-bottom: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #191f28;
  margin: 0 0 12px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  background: white;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid #e5e7eb;
}

.stat-label {
  font-size: 11px;
  color: #8b95a1;
  font-weight: 600;
}

.stat-value {
  font-size: 14px;
  color: #191f28;
  font-weight: 700;
}

/* 마크다운 스타일 */
.markdown-content {
  background: white;
  padding: 14px;
  border-radius: 8px;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
  border: 1px solid #e5e7eb;
  max-height: 300px;
  overflow-y: auto;
}

/* 마크다운 제목 스타일 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin: 12px 0 8px 0;
  font-weight: 700;
  color: #191f28;
}

.markdown-content :deep(h1) {
  font-size: 16px;
  border-bottom: 2px solid #3182f6;
  padding-bottom: 6px;
}

.markdown-content :deep(h2) {
  font-size: 14px;
  border-left: 4px solid #3182f6;
  padding-left: 8px;
}

.markdown-content :deep(h3) {
  font-size: 13px;
  color: #3182f6;
}

/* 마크다운 단락 */
.markdown-content :deep(p) {
  margin: 8px 0;
}

/* 마크다운 리스트 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

/* 마크다운 코드 */
.markdown-content :deep(code) {
  background: #f0f4ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  color: #d63031;
}

.markdown-content :deep(pre) {
  background: #2d3436;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  color: #dfe6e9;
  background: transparent;
  padding: 0;
}

.detail-footer {
  text-align: right;
}

.created-at {
  font-size: 11px;
  color: #a8adb8;
}

/* 로딩 & Empty 상태 */
.state-area {
  text-align: center;
  padding: 40px 20px;
}

.empty-text {
  font-size: 13px;
  color: #adb5bd;
  margin: 0;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e8eb;
  border-top-color: #3182f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    max-height: 500px;
    transform: translateY(0);
  }
}

/* 팝업 애니메이션 */
.expand-enter-active, .expand-leave-active {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.expand-enter-from, .expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 스크롤바 커스텀 */
.markdown-content::-webkit-scrollbar {
  width: 6px;
}

.markdown-content::-webkit-scrollbar-track {
  background: transparent;
}

.markdown-content::-webkit-scrollbar-thumb {
  background: #d1d6db;
  border-radius: 3px;
}

.markdown-content::-webkit-scrollbar-thumb:hover {
  background: #8b95a1;
}
</style>