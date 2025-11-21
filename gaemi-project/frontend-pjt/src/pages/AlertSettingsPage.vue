<template>
  <div class="page-container">
    <div class="grid">
      <AlertForm :stocks="stocks" @create="addAlert" />
      <AlertList :items="alerts" @toggle="toggleAlert" @remove="removeAlert" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AlertForm from '@/components/alerts/AlertForm.vue';
import AlertList from '@/components/alerts/AlertList.vue';

const stocks = [
  { code: '005930', name: '삼성전자' },
  { code: '000660', name: 'SK하이닉스' },
  { code: '035420', name: 'NAVER' }
];

const alerts = ref([
  {
    id: 1,
    stock: '005930',
    stockName: '삼성전자',
    enabled: true,
    description: '이상: 80,000원'
  },
  {
    id: 2,
    stock: '000660',
    stockName: 'SK하이닉스',
    enabled: true,
    description: '이하: 130,000원'
  }
]);

function addAlert(form) {
  const stockMeta = stocks.find(s => s.code === form.stock);
  alerts.value.push({
    id: Date.now(),
    stock: form.stock,
    stockName: stockMeta?.name ?? form.stock,
    enabled: true,
    description: buildDescription(form)
  });
}

function buildDescription(form) {
  const condMap = {
    gte: '이상',
    lte: '이하',
    changeUp: '상승률 이상',
    changeDown: '하락률 이하'
  };
  return `${condMap[form.condition]}: ${form.target}`;
}

function toggleAlert(item) {
  console.log('toggle', item.id, item.enabled);
}

function removeAlert(id) {
  alerts.value = alerts.value.filter(a => a.id !== id);
}
</script>

<style scoped>
.page-container {
  width: 100%;
}

.grid {
  display: grid;
  grid-template-columns: 1.2fr 1.1fr;
  gap: 20px;
}
@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>