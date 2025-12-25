<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">알림 관리</h1>
      <p class="page-desc">관심 종목의 시세 변화를 놓치지 마세요</p>
    </div>

    <div class="content-grid">
      <section class="section-card left-section">
        <div class="section-header">
          <h2 class="section-title">내 관심 종목</h2>
          <span class="count">{{ favoriteStocks.length }}개</span>
        </div>

        <div v-if="favoriteStocks.length > 0" class="favorite-list">
          <div
            v-for="item in favoriteStocks"
            :key="item.code"
            class="favorite-item"
          >
            <div class="item-info">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-code">{{ item.code }}</span>
            </div>
            <button 
              class="delete-btn" 
              @click="openDeleteModal('favorite', item.code)"
              title="삭제"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>등록된 관심 종목이 없습니다.</p>
        </div>
      </section>

      <section class="section-card right-section">
        <div class="section-header">
          <h2 class="section-title">알림 조건 설정</h2>
        </div>

        <AlertForm 
          :stocks="favoriteStocks" 
          :initial-code="targetStockCode"
          @create="addAlert" 
        />

        <div class="divider"></div>

        <AlertList
          v-if="!alertsStore.isLoading"
          :items="alerts"
          @remove="(id) => openDeleteModal('alert', id)"
          @toggle="toggleAlert"
        />
        <div v-else class="loading-state">
          알림 목록을 불러오는 중...
        </div>
      </section>
    </div>

    <transition name="modal-fade">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-card">
          <div class="modal-icon warning">⚠️</div>
          
          <h3 class="modal-title">{{ deleteModalTitle }}</h3>
          <p class="modal-desc" v-html="deleteModalDesc"></p>

          <div class="modal-actions">
            <button class="btn-cancel" @click="closeDeleteModal">취소</button>
            <button class="btn-delete" @click="confirmDelete">삭제할래요</button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useFavoritesStore } from "@/stores/favoritesStore.js";
import { useAlertsStore } from "@/stores/alertsStore.js";
import { useToastStore } from "@/stores/toastStore.js";
import AlertForm from "@/components/alerts/AlertForm.vue";
import AlertList from "@/components/alerts/AlertList.vue";

const route = useRoute();
const store = useFavoritesStore();
const alertsStore = useAlertsStore();
const toastStore = useToastStore();
const targetStockCode = ref(""); 

/* --------------------------------------------------
   🗑️ 삭제 모달 관련 상태 & 로직
-------------------------------------------------- */
const showDeleteModal = ref(false);
const deleteTargetType = ref(""); // 'favorite' 또는 'alert'
const deleteTargetId = ref(null); // 삭제할 대상의 ID 또는 Code

// 모달 제목 (Computed)
const deleteModalTitle = computed(() => {
  return deleteTargetType.value === 'favorite' 
    ? "관심 종목을 삭제할까요?" 
    : "알림을 삭제할까요?";
});

// 모달 설명 (Computed)
const deleteModalDesc = computed(() => {
  if (deleteTargetType.value === 'favorite') {
    return `관심 종목을 삭제하면<br/><strong>설정해둔 알림 조건도 모두 함께 삭제</strong>돼요.`;
  } else {
    return `선택하신 알림 조건을<br/><strong>정말로 삭제하시겠습니까?</strong>`;
  }
});

// 삭제 모달 열기
function openDeleteModal(type, id) {
  // 관심종목 삭제인데 알림이 하나도 없는 경우 -> 그냥 바로 삭제 (모달 없이 편의성 제공)
  // (만약 무조건 물어보고 싶으면 이 if문 제거하세요)
  if (type === 'favorite' && !alertsStore.hasAlertsForStock(id)) {
    store.removeFavorite(id);
    return;
  }

  deleteTargetType.value = type;
  deleteTargetId.value = id;
  showDeleteModal.value = true;
}

// 모달 닫기
function closeDeleteModal() {
  showDeleteModal.value = false;
  deleteTargetType.value = "";
  deleteTargetId.value = null;
}

// 진짜 삭제 실행
function confirmDelete() {
  try {
    if (deleteTargetType.value === 'favorite') {
      // 관심 종목 + 관련 알림 모두 삭제
      const favoriteStock = favoriteStocks.value.find(s => s.code === deleteTargetId.value);
      alertsStore.removeByStockCode(deleteTargetId.value);
      store.removeFavorite(deleteTargetId.value);

      // ✅ 성공 토스트
      toastStore.add({
        type: "success",
        title: "관심종목 삭제됨",
        message: `${favoriteStock?.name || deleteTargetId.value}이(가) 관심종목에서 제거되었습니다.`,
        duration: 3000,
      });
    } else if (deleteTargetType.value === 'alert') {
      // 특정 알림 1개만 삭제
      const alert = alerts.value.find(a => a.id === deleteTargetId.value);
      alertsStore.removeAlert(deleteTargetId.value);

      // ✅ 성공 토스트
      toastStore.add({
        type: "success",
        title: "알림 삭제됨",
        message: `${alert?.stockName} 알림이 삭제되었습니다.`,
        duration: 3000,
      });
    }
  } catch (error) {
    // ❌ 오류 토스트
    toastStore.add({
      type: "error",
      title: "삭제 실패",
      message: error.message || "항목을 삭제할 수 없습니다.",
      duration: 4000,
    });
  }

  closeDeleteModal();
}

/* --------------------------------------------------
   기타 로직 (기존 유지)
-------------------------------------------------- */
const stocks = [
  { code: "005930", name: "삼성전자" },
  { code: "000660", name: "SK하이닉스" },
  { code: "035420", name: "NAVER" },
  { code: "006400", name: "삼성SDI" },
  { code: "005380", name: "현대차" },
  { code: "035720", name: "카카오" },
];

onMounted(() => {
  alertsStore.fetchAlerts();
  if (route.query.code) {
    targetStockCode.value = route.query.code;
  }
});

const favoriteStocks = computed(() => {
  return store.favorites
    .map((item) => {
      const code = typeof item === "string" ? item : item.code;
      return stocks.find((s) => s.code === code) || { code, name: code }; 
    })
    .filter((s) => s.code);
});

const alerts = computed(() => {
  return alertsStore.alerts.map((a) => {
    const stock = stocks.find((s) => s.code === a.stockCode);
    return {
      ...a,
      stockName: a.stockName || stock?.name || a.stockCode, 
      description: formatDescription(a), 
    };
  });
});

function formatDescription(alert) {
  if (alert.description) return alert.description;
  const condMap = {
    gte: "이상",
    lte: "이하",
    changeUp: "% 이상 급등",
    changeDown: "% 이상 급락"
  };
  const unit = (alert.condition === 'changeUp' || alert.condition === 'changeDown') ? '' : '원';
  return `${alert.target}${unit} ${condMap[alert.condition] || ''}`;
}

function toggleAlert(item) {
  alertsStore.toggleAlert(item.id);
}

function addAlert(alert) {
  try {
    const stockObj = favoriteStocks.value.find(s => s.code === alert.stock);
    
    // 조건 매핑: 프론트 조건 -> 백엔드 형식 (metric_type, operator, target_value)
    const conditionMap = {
      gte: { metric_type: 'price', operator: '>=', target_value: alert.target.toString() },
      lte: { metric_type: 'price', operator: '<=', target_value: alert.target.toString() },
      changeUp: { metric_type: 'change_rate', operator: '>=', target_value: alert.target.toString() },
      changeDown: { metric_type: 'change_rate', operator: '<=', target_value: (-alert.target).toString() },
    };
    
    const conditionData = conditionMap[alert.condition] || conditionMap.gte;
    
    alertsStore.addAlert({
      stockCode: alert.stock,
      stockName: stockObj?.name || alert.stock,
      condition: alert.condition,
      target: alert.target,
      // 백엔드 필드
      metric_type: conditionData.metric_type,
      operator: conditionData.operator,
      target_value: conditionData.target_value,
    });
    
    // ✅ 성공 토스트 표시
    toastStore.add({
      type: "success",
      title: "알림 추가됨",
      message: `${stockObj?.name || alert.stock}의 가격 알림이 설정되었습니다.`,
      duration: 3000,
    });
  } catch (error) {
    // ❌ 오류 토스트 표시
    toastStore.add({
      type: "error",
      title: "알림 추가 실패",
      message: error.message || "알림을 추가할 수 없습니다.",
      duration: 4000,
    });
  }
}
</script>

<style scoped>
/* 기존 스타일 그대로 유지 */
.settings-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}
.page-header {
  text-align: center;
  margin-bottom: 40px;
}
.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #191f28;
  margin-bottom: 8px;
}
.page-desc {
  font-size: 16px;
  color: #8b95a1;
}
.content-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
}
.section-card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e8eb;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.count {
  font-size: 13px;
  font-weight: 600;
  color: #3182f6;
  background: rgba(49, 130, 246, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
}
.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  background: #f9fafb;
  transition: background 0.2s;
}
.favorite-item:hover {
  background: #f2f4f6;
}
.item-name {
  font-weight: 600;
  font-size: 15px;
  color: #333;
}
.item-code {
  font-size: 12px;
  color: #8b95a1;
  margin-left: 6px;
}
.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #adb5bd;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}
.delete-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}
.empty-state {
  text-align: center;
  padding: 30px;
  color: #adb5bd;
  font-size: 14px;
}
.divider {
  height: 1px;
  background: #f2f4f6;
  margin: 32px 0;
}
.loading-state {
  text-align: center;
  padding: 40px;
  color: #8b95a1;
  font-size: 14px;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: white;
  width: 90%;
  max-width: 320px;
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes modalPop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.modal-icon {
  font-size: 40px;
  margin-bottom: 16px;
}
.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #191f28;
  margin-bottom: 8px;
}
.modal-desc {
  font-size: 15px;
  color: #6b7684;
  line-height: 1.5;
  margin-bottom: 24px;
}
/* v-html 내부 strong 태그 스타일링을 위해 global deep selector나 그냥 일반 css 필요하지만, 
   scoped 내에서는 :deep() 사용 */
.modal-desc :deep(strong) {
  color: #ef4444;
  font-weight: 600;
}
.modal-actions {
  display: flex;
  gap: 12px;
}
.btn-cancel, .btn-delete {
  flex: 1;
  padding: 14px 0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
}
.btn-cancel {
  background: #f2f4f6;
  color: #4e5968;
}
.btn-delete {
  background: #ef4444;
  color: white;
}
.btn-cancel:hover, .btn-delete:hover {
  opacity: 0.9;
}
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .settings-page {
    padding: 20px;
  }
}
</style>