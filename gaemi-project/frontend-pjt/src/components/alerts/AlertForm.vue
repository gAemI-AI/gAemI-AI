<template>
  <div class="alert-form-card">
    <h3 class="form-title">새 알림 추가</h3>
    
    <form @submit.prevent="submit" class="form-body">
      
      <div class="form-group" ref="stockDropdownRef">
        <label>어떤 종목을 지켜볼까요?</label>
        
        <div class="custom-select-container">
          <div 
            class="select-trigger" 
            :class="{ active: isStockOpen }" 
            @click="toggleStockDropdown"
          >
            <span v-if="selectedStockName" class="selected-text">
              {{ selectedStockName }} <span class="code-badge">{{ form.stock }}</span>
            </span>
            <span v-else class="placeholder">종목을 선택하거나 검색하세요</span>
            <span class="arrow" :class="{ rotated: isStockOpen }">▼</span>
          </div>

          <transition name="dropdown-fade">
            <div v-if="isStockOpen" class="dropdown-menu">
              <div class="search-box">
                <span class="search-icon">🔍</span>
                <input 
                  ref="searchInputRef"
                  v-model="searchKeyword" 
                  type="text" 
                  placeholder="종목명 또는 코드 검색"
                  @click.stop
                />
              </div>

              <ul class="options-list">
                <li 
                  v-for="s in filteredStocks" 
                  :key="s.code" 
                  class="option-item"
                  :class="{ selected: s.code === form.stock }"
                  @click="selectStock(s)"
                >
                  <span class="name">{{ s.name }}</span>
                  <span class="code">{{ s.code }}</span>
                  <span v-if="s.code === form.stock" class="check-icon">✔</span>
                </li>

                <li v-if="filteredStocks.length === 0" class="no-result">
                  검색 결과가 없어요 🥲
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>

      <div class="form-group" ref="conditionDropdownRef">
        <label>어떤 조건일 때 알려드릴까요?</label>
        
        <div class="custom-select-container">
          <div 
            class="select-trigger" 
            :class="{ active: isConditionOpen }" 
            @click="toggleConditionDropdown"
          >
            <span class="selected-text">{{ selectedConditionLabel }}</span>
            <span class="arrow" :class="{ rotated: isConditionOpen }">▼</span>
          </div>

          <transition name="dropdown-fade">
            <div v-if="isConditionOpen" class="dropdown-menu">
              <ul class="options-list">
                <li 
                  v-for="opt in conditionOptions" 
                  :key="opt.value" 
                  class="option-item"
                  :class="{ selected: opt.value === form.condition }"
                  @click="selectCondition(opt)"
                >
                  <span class="name">{{ opt.label }}</span>
                  <span v-if="opt.value === form.condition" class="check-icon">✔</span>
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>

      <div class="form-group">
        <label>목표값 입력</label>
        <div class="input-wrapper">
          <input
            v-model.number="form.target"
            type="number"
            placeholder="예: 80000"
            required
            class="target-input"
          />
          <span class="unit">{{ unitText }}</span>
        </div>
      </div>

      <button type="submit" class="submit-btn">
        알림 받기
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref, onMounted, onUnmounted, nextTick } from 'vue';

const props = defineProps({
  stocks: { type: Array, required: true },
  initialCode: { type: String, default: '' },
});

const emit = defineEmits(['create']);

/* -------------------------------------
   데이터 & 상태
------------------------------------- */
const form = reactive({
  stock: props.initialCode || '',
  condition: 'gte',
  target: null,
});

const conditionOptions = [
  { value: 'gte', label: '특정 가격 이상일 때' },
  { value: 'lte', label: '특정 가격 이하일 때' },
  { value: 'changeUp', label: '전일 대비 급등했을 때 (%)' },
  { value: 'changeDown', label: '전일 대비 급락했을 때 (%)' },
];

const isStockOpen = ref(false);
const isConditionOpen = ref(false);

const stockDropdownRef = ref(null);
const conditionDropdownRef = ref(null);
const searchInputRef = ref(null);

const searchKeyword = ref("");

/* -------------------------------------
   Computed
------------------------------------- */
const selectedStockName = computed(() => {
  const found = props.stocks.find(s => s.code === form.stock);
  return found ? found.name : '';
});

const selectedConditionLabel = computed(() => {
  const found = conditionOptions.find(opt => opt.value === form.condition);
  return found ? found.label : '조건 선택';
});

const unitText = computed(() => {
  if (form.condition === 'changeUp' || form.condition === 'changeDown') return '%';
  return '원';
});

const filteredStocks = computed(() => {
  if (!searchKeyword.value) return props.stocks;
  const keyword = searchKeyword.value.toLowerCase();
  return props.stocks.filter(s => 
    s.name.toLowerCase().includes(keyword) || 
    s.code.includes(keyword)
  );
});

/* -------------------------------------
   Methods
------------------------------------- */
watch(() => props.initialCode, (newCode) => {
  if (newCode) form.stock = newCode;
});

function toggleStockDropdown() {
  if (isStockOpen.value) {
    isStockOpen.value = false;
  } else {
    isStockOpen.value = true;
    isConditionOpen.value = false; 
    searchKeyword.value = "";
    nextTick(() => searchInputRef.value?.focus());
  }
}

function selectStock(stock) {
  form.stock = stock.code;
  isStockOpen.value = false;
}

function toggleConditionDropdown() {
  if (isConditionOpen.value) {
    isConditionOpen.value = false;
  } else {
    isConditionOpen.value = true;
    isStockOpen.value = false;
  }
}

function selectCondition(option) {
  form.condition = option.value;
  isConditionOpen.value = false;
}

function handleClickOutside(event) {
  if (stockDropdownRef.value && !stockDropdownRef.value.contains(event.target)) {
    isStockOpen.value = false;
  }
  if (conditionDropdownRef.value && !conditionDropdownRef.value.contains(event.target)) {
    isConditionOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

function submit() {
  if (!form.stock || !form.target) {
    // 검증 오류는 토스트로 표시 (AlertSettingsPage에서 처리)
    return;
  }
  emit('create', { ...form });
  
  form.target = null;
}
</script>

<style scoped>
.alert-form-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #e5e8eb;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.form-title {
  font-size: 16px;
  font-weight: 700;
  color: #191f28;
  margin-bottom: 20px;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #4e5968;
  margin-bottom: 8px;
}

/* =========================================
   😎 커스텀 드롭다운 공통 스타일
========================================= */
.custom-select-container {
  position: relative;
}

.select-trigger {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #d1d6db;
  background: white;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  height: 48px;
  box-sizing: border-box;
}

.select-trigger:hover {
  background: #f9fafb;
}

.select-trigger.active {
  border-color: #3182f6;
  box-shadow: 0 0 0 2px rgba(49, 130, 246, 0.1);
}

.selected-text {
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
  display: flex;
  align-items: center;
  gap: 6px;
}

.code-badge {
  font-size: 12px;
  color: #8b95a1;
  background: #f2f4f6;
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 500;
}

.placeholder {
  color: #adb5bd;
  font-size: 14px;
}

.arrow {
  font-size: 10px;
  color: #8b95a1;
  transition: transform 0.2s;
}

.arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  border: 1px solid #f2f4f6;
  z-index: 50;
  overflow: hidden;
  animation: slideDown 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.search-box {
  padding: 10px;
  border-bottom: 1px solid #f2f4f6;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f9fafb;
}

.search-icon {
  font-size: 14px;
}

.search-box input {
  border: none;
  background: transparent;
  width: 100%;
  font-size: 14px;
  outline: none;
  padding: 4px;
}

.options-list {
  max-height: 240px;
  overflow-y: auto;
  margin: 0;
  padding: 0;
  list-style: none;
}

.option-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: background 0.1s;
}

.option-item:hover {
  background: #f2f4f6;
}

.option-item.selected {
  background: #eef4ff;
}

.option-item .name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.option-item .code {
  font-size: 12px;
  color: #8b95a1;
}

.check-icon {
  margin-left: auto;
  font-size: 12px;
  color: #3182f6;
}

.no-result {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: #9ca3af;
}

/* =========================================
   📝 Input 스타일 (CSS 수정됨)
========================================= */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.target-input {
  width: 100%;
  padding: 12px 16px;
  /* ✅ [수정] 오른쪽 여백을 넉넉히 줘서 '원' 글자가 겹치지 않게 함 */
  padding-right: 48px; 
  border-radius: 12px;
  border: 1px solid #d1d6db;
  background: white;
  font-size: 15px;
  color: #333;
  outline: none;
  height: 48px;
  transition: all 0.2s;
}

.target-input:focus {
  border-color: #3182f6;
  box-shadow: 0 0 0 2px rgba(49, 130, 246, 0.1);
}

/* ✅ [추가] 브라우저 기본 화살표(스피너) 제거 */
.target-input::-webkit-outer-spin-button,
.target-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.target-input {
  -moz-appearance: textfield;
}

.unit {
  position: absolute;
  right: 16px;
  font-size: 14px;
  color: #8b95a1;
  font-weight: 600;
  pointer-events: none; /* 클릭 통과 */
}

/* 버튼 */
.submit-btn {
  margin-top: 12px;
  width: 100%;
  padding: 16px;
  background: #3182f6;
  color: white;
  font-size: 16px;
  font-weight: 700;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 4px 12px rgba(49, 130, 246, 0.2);
}

.submit-btn:hover {
  background: #1b64da;
  transform: translateY(-1px);
}
.submit-btn:active {
  transform: translateY(0);
}
</style>