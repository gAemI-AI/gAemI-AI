<template>
  <div class="auth-layout">
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
</script>

<style>
.auth-layout {
  min-height: 100vh;
  background: #f5f6fa;

  display: flex;
  align-items: center;
  justify-content: center;
}

/* ✅ 깨지는 input들 공통 해결 */
.auth-layout input {
  min-width: 0;     /* flex overflow 방지 */
  width: auto;      /* width:100% 덮어쓰기 */
  flex: 1;          /* 버튼/아이콘 옆에서 정상 축소 */
}
</style>
