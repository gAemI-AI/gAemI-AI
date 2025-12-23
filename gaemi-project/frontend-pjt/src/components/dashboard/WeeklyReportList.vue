<template>
  <div class="panel-box">
    <div class="panel-header">
      <h3 class="panel-title">주간 리포트</h3>
      <span v-if="reports.length > 0" class="badge">NEW</span>
    </div>

    <div v-if="isLoading" class="state-area">
      <div class="spinner"></div>
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
          <div class="card-icon">📄</div>
          <div class="card-info">
            <span class="stock-name">{{ report.stock?.stock_name || report.stock_name }}</span>
            <span class="report-date">{{ formatDate(report.start_date) }} 주차</span>
          </div>
          <div class="arrow-indicator">›</div>
        </div>

        <transition name="pop">
          <div 
            v-if="selectedReportId === report.id" 
            class="bubble-popup"
            @click.stop
          >
            <div class="bubble-header">
              <h4>{{ report.title || '주간 이슈 요약' }}</h4>
            </div>
            
            <p class="bubble-summary">{{ report.summary }}</p>
            
            </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { fetchWeeklyReports } from '@/api/reports';

const reports = ref([]);
const isLoading = ref(false);
const selectedReportId = ref(null);

const loadReports = async () => {
  isLoading.value = true;
  try {
    const data = await fetchWeeklyReports();
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

// 날짜 포맷 (YYYY-MM-DD -> MM/DD)
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()}`;
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
/* ✅ 박스 디자인 통일 (DashboardPage의 .chart-box 등과 동일한 스타일) */
.panel-box {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 20px;
  /* 그림자는 취향에 따라 추가/제거 */
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02); */
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
  font-size: 10px;
  background: #ff5252;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.report-card-wrapper {
  position: relative;
}

/* 리포트 카드 (내부 아이템) */
.report-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f9fafb; /* 살짝 회색 배경으로 구분 */
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid transparent; /* 호버 시 색상 변화를 위해 */
  cursor: pointer;
  transition: all 0.2s ease;
}

.report-card:hover, .report-card.active {
  background: white;
  border-color: #3182f6;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.1);
}

.card-icon {
  font-size: 20px;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stock-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.report-date {
  font-size: 12px;
  color: #8b95a1;
  margin-top: 2px;
}

.arrow-indicator {
  color: #d1d6db;
  font-size: 18px;
}

/* 💬 말풍선 팝업 */
.bubble-popup {
  position: absolute;
  left: calc(100% + 12px); 
  top: 0;
  width: 240px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e8eb;
  z-index: 100;
}

/* 말풍선 꼬리 */
.bubble-popup::before {
  content: "";
  position: absolute;
  top: 20px;
  right: 100%;
  margin-top: -6px;
  border-width: 6px;
  border-style: solid;
  border-color: transparent white transparent transparent;
  filter: drop-shadow(-1px 0 0 #e5e8eb);
}

.bubble-header {
  margin-bottom: 8px;
}

.bubble-header h4 {
  font-size: 14px;
  font-weight: 700;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.bubble-summary {
  font-size: 13px;
  color: #6b7684;
  line-height: 1.5;
  margin: 0;
  /* 내용이 길면 스크롤 혹은 말줄임 */
  max-height: 120px;
  overflow-y: auto;
}

/* 로딩 & Empty 상태 */
.state-area {
  text-align: center;
  padding: 24px 0;
}

.empty-text {
  font-size: 13px;
  color: #adb5bd;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e8eb;
  border-top-color: #3182f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 팝업 애니메이션 */
.pop-enter-active, .pop-leave-active {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.pop-enter-from, .pop-leave-to {
  opacity: 0;
  transform: translateX(-10px) scale(0.95);
}
</style>