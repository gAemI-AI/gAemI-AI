<template>
  <form class="form" @submit.prevent="submit">
    <div class="field">
      <label>종목 선택</label>
      <select v-model="form.stock" required>
        <option value="" disabled>종목을 선택하세요</option>
        <option v-for="s in stocks" :key="s.code" :value="s.code">
          {{ s.name }}
        </option>
      </select>
    </div>

    <div class="field">
      <label>조건</label>
      <select v-model="form.condition" required>
        <option value="gte">가격 이상</option>
        <option value="lte">가격 이하</option>
        <option value="changeUp">전일 대비 상승률 이상</option>
        <option value="changeDown">전일 대비 하락률 이하</option>
      </select>
    </div>

    <div class="field">
      <label>목표 값</label>
      <input
        v-model.number="form.target"
        type="number"
        placeholder="예: 80000"
        required
      />
    </div>

    <button type="submit" class="submit-btn">알림 추가</button>
  </form>
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  stocks: { type: Array, required: true },
});
const emit = defineEmits(['create']);

const form = reactive({
  stock: '',
  condition: 'gte',
  target: null,
});

function submit() {
  emit('create', { ...form });
  form.stock = '';
  form.condition = 'gte';
  form.target = null;
}
</script>

<style scoped>
.form {
  background: white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
label {
  font-size: 13px;
  color: #4b5563;
}
select,
input {
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 6px 8px;
  font-size: 13px;
}
.submit-btn {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 10px;
  border: none;
  background: #2563eb;
  color: white;
  cursor: pointer;
  font-size: 14px;
}
</style>
