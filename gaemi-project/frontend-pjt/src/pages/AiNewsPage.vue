<template>
  <div class="page-container">
    <header class="header">
      <div>
        <h2>AI 뉴스 분석</h2>
        <p>API가 제공하는 뉴스에 감정 분석을 적용한 결과입니다.</p>
      </div>
      <button class="refresh-btn">실시간 업데이트</button>
    </header>

    <AiNewsList :items="newsItems" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AiNewsList from '@/components/news/AiNewsList.vue';

const newsItems = ref([
  {
    id: 1,
    stock: '삼성전자',
    sentimentLabel: '긍정',
    sentimentClass: 'positive',
    type: '실적',
    title: '삼성전자, 3분기 영업이익 10조원대 기록',
    summary:
      '3분기 영업이익이 예상치를 상회하며 반도체 업황 회복 기대감이 커지고 있습니다.',
    source: '전자신문',
    time: '오전 10:21'
  },
  {
    id: 2,
    stock: 'SK하이닉스',
    sentimentLabel: '부정',
    sentimentClass: 'negative',
    type: '공급',
    title: 'SK하이닉스, 미국 정부 수출 규제 강화 우려',
    summary:
      '미국의 추가 수출 규제가 제기되며 단기적인 실적 변동성이 확대될 수 있다는 분석입니다.',
    source: 'Reuters',
    time: '오전 09:51'
  }
]);
</script>

<style scoped>
.page-container {
  width: 100%;
}

/* 기존 그대로 유지 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header h2 {
  font-size: 18px;
  font-weight: 600;
}
.header p {
  font-size: 13px;
  color: #6b7280;
}
.refresh-btn {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  font-size: 13px;
}
</style>
