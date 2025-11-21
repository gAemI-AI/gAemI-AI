<template>
  <div class="page-container">
    <div class="grid">
      <section class="left">
        <h2 class="section-title">실시간 시세</h2>
        <StockTickerRow
          :stocks="stocks"
          :selected-code="selectedStock.code"
          @select="onSelectStock"
        />

        <div class="detail-wrapper">
          <StockDetailCard :stock="selectedStock" />
        </div>
      </section>

      <aside class="right">
        <AlertHistoryList :alerts="alerts" />
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import StockTickerRow from '@/components/dashboard/StockTickerRow.vue';
import StockDetailCard from '@/components/dashboard/StockDetailCard.vue';
import AlertHistoryList from '@/components/dashboard/AlertHistoryList.vue';

const stocks = [
  { code: '005930', name: '삼성전자', price: 70680, change: -1320, changeRate: -1.83 },
  { code: '000660', name: 'SK하이닉스', price: 139421, change: 579, changeRate: 0.41 },
  { code: '035420', name: 'NAVER', price: 215222, change: 3722, changeRate: 1.76 },
  { code: '006400', name: '삼성SDI', price: 386519, change: -6481, changeRate: -1.65 },
  { code: '005380', name: '현대차', price: 195740, change: 3240, changeRate: 1.68 }
];

const alerts = ref([
  {
    id: 1,
    stockName: '삼성전자',
    statusClass: 'working',
    title: '목표가 75,000원 도달 시 알림',
    time: '5분 전'
  },
  {
    id: 2,
    stockName: 'SK하이닉스',
    statusClass: 'working',
    title: '2% 이상 하락 알림',
    time: '15분 전'
  },
  {
    id: 3,
    stockName: 'NAVER',
    statusClass: 'working',
    title: '평균 거래량 200% 초과',
    time: '1시간 전'
  }
]);

const selectedStock = ref(stocks[0]);

function onSelectStock(stock) {
  selectedStock.value = stock;
}
</script>

<style scoped>
.page-container {
  width: 100%;
}

.grid {
  display: grid;
  grid-template-columns: 3fr 1.2fr;
  gap: 20px;
}

.left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.detail-wrapper {
  margin-top: 8px;
}

.right {
  min-width: 280px;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
