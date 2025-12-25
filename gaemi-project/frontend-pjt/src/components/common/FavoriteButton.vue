<!-- src/components/common/FavoriteButton.vue -->
<template>
  <button class="star-btn" @click="toggleFavorite" :disabled="isLoading">
    <span :class="{ active: isFavorite }">★</span>
  </button>
</template>

<script setup>
import { computed, ref } from "vue";
import { useFavoritesStore } from "@/stores/favoritesStore.js";

const props = defineProps({
  stock: { type: Object, required: true },
});

const store = useFavoritesStore();
const isLoading = ref(false);

// ✔ store는 코드 기반으로 저장하므로 코드 비교만 하면 됨!
const isFavorite = computed(() =>
  store.favorites.includes(props.stock.code)
);

async function toggleFavorite() {
  isLoading.value = true;
  try {
    const accessToken = localStorage.getItem("accessToken");
    if (!accessToken) {
      alert("로그인이 필요합니다.");
      return;
    }

    if (isFavorite.value) {
      // ❌ 관심종목 삭제 (DELETE /api/v1/watchlist/{stock_code}/)
      const response = await fetch(
        `http://localhost:8000/api/v1/watchlist/${props.stock.code}/`,
        {
          method: "DELETE",
          headers: {
            "Authorization": `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok || response.status === 204) {
        store.removeFavorite(props.stock.code);
      } else {
        console.error("관심종목 삭제 실패:", response.status);
        alert("관심종목 삭제에 실패했습니다.");
      }
    } else {
      // ⭐ 관심종목 추가 (POST /api/v1/watchlist/)
      const response = await fetch(
        "http://localhost:8000/api/v1/watchlist/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            stock: props.stock.code,
          }),
        }
      );

      if (response.ok) {
        store.addFavorite(props.stock.code);
      } else {
        const errorData = await response.json();
        console.error("관심종목 추가 실패:", errorData);
        alert("관심종목 추가에 실패했습니다.");
      }
    }
  } catch (error) {
    console.error("토글 오류:", error);
    alert("오류가 발생했습니다.");
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.star-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 24px;
  padding: 4px;
  transition: opacity 0.2s ease;
}

.star-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.star-btn span {
  color: #d1d5db;
  transition: color 0.2s ease;
}

.star-btn span.active {
  color: #2563eb;
}
</style>
