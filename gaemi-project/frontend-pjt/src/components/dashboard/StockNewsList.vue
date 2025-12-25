<template>
  <div class="news-section">
    <div class="section-header">
      <h3>AI 요약 뉴스</h3>
      <span v-if="newsList.length > 0" class="badge">최신 {{ newsList.length }}건</span>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>관련 뉴스를 분석하고 있어요...</p>
    </div>

    <div v-else-if="newsList.length === 0" class="empty-state">
      <p>최근 24시간 내 주요 뉴스가 없습니다 🍃</p>
    </div>

    <div v-else class="news-list">
      <div 
        v-for="(news, index) in newsList" 
        :key="index" 
        class="news-item"
        @click="openLink(news.link)"
      >
        <div class="news-content">
          <h4 class="news-title" v-html="news.title"></h4>
          
          <div v-if="hasSummary(news.summary)" class="summary-container">
            <p 
              v-for="(line, idx) in parseSummary(news.summary)" 
              :key="idx" 
              class="summary-line"
            >
              • {{ line }}
            </p>
          </div>

          <div class="news-meta">
            <span class="source">{{ news.press || '뉴스' }}</span>
            <span class="dot">·</span>
            <span class="date">{{ formatDate(news.pubDate) }}</span>
          </div>
        </div>
        
        <div class="arrow-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { fetchStockNews } from '@/api/stocks';

const props = defineProps({
  stockCode: { type: String, required: true },
});

const newsList = ref([]);
const isLoading = ref(false);

const loadNews = async () => {
  if (!props.stockCode) return;
  isLoading.value = true;
  newsList.value = [];

  try {
    const res = await fetchStockNews(props.stockCode);
    const list = res.data || [];
    newsList.value = list.slice(0, 3);
  } catch (error) {
    console.error("뉴스 로드 실패:", error);
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.stockCode, () => {
  loadNews();
}, { immediate: true });

const openLink = (url) => {
  if (url) window.open(url, '_blank');
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  return `${date.getMonth() + 1}월 ${date.getDate()}일`;
};

// ✅ [추가] 요약문이 유효한지 확인 (빈 배열 [] 이면 false)
const hasSummary = (summary) => {
  const parsed = parseSummary(summary);
  return parsed && parsed.length > 0;
};

// ✅ [추가] 요약 데이터 파싱 (문자열인 경우 배열로 변환 시도)
const parseSummary = (summary) => {
  if (!summary) return [];
  
  // 이미 배열인 경우 바로 반환
  if (Array.isArray(summary)) {
    return summary.filter(s => s && s.trim() !== ""); // 빈 문자열 제거
  }

  // 만약 DB에서 "['요약1', '요약2']" 형태의 문자열로 온다면 파싱 시도
  if (typeof summary === 'string') {
    // 빈 괄호 문자열 처리
    if (summary === '[]') return [];
    
    // JSON 파싱 시도 (따옴표 처리)
    try {
      // 파이썬 리스트 스트링(싱글쿼트)일 경우 더블쿼트로 변환 후 파싱
      const jsonStr = summary.replace(/'/g, '"');
      const parsed = JSON.parse(jsonStr);
      if (Array.isArray(parsed)) return parsed;
    } catch (e) {
      // 파싱 실패 시 그냥 문자열 하나로 취급
      return [summary];
    }
  }
  
  return [];
};
</script>

<style scoped>
.news-section {
  margin-top: 24px;
  background: white;
  border-top: 1px solid #f2f4f6;
  padding-top: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: #191f28;
  margin: 0;
}

.badge {
  font-size: 11px;
  color: #3182f6;
  background: rgba(49, 130, 246, 0.1);
  padding: 3px 6px;
  border-radius: 6px;
  font-weight: 600;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* 상단 정렬 */
  padding: 16px;
  border-radius: 16px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.news-item:hover {
  background: #f2f4f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.news-content {
  flex: 1;
  padding-right: 16px;
  min-width: 0;
}

.news-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
  word-break: keep-all; /* 단어 단위 줄바꿈 */
}

/* ✅ 요약문 스타일 개선 */
.summary-container {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-line {
  font-size: 13px;
  color: #596472; /* 조금 더 진한 회색 */
  line-height: 1.5;
  margin: 0;
  padding-left: 4px;
  letter-spacing: -0.2px;
}

.news-meta {
  font-size: 12px;
  color: #8b95a1;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.arrow-icon {
  color: #b0b8c1;
  display: flex;
  align-items: center;
  margin-top: 2px; /* 제목 높이에 맞춤 */
}

.loading-state, .empty-state {
  text-align: center;
  padding: 32px 0;
  color: #8b95a1;
  font-size: 13px;
  background: #f9fafb;
  border-radius: 12px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e8eb;
  border-top-color: #3182f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>