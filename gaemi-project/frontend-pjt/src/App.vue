<template>
  <RouterView />
  <ToastStack />
</template>

<script setup>
import { RouterView } from "vue-router";
import ToastStack from "@/components/toast/ToastStack.vue";
</script>

<style>
/* App에서 layout 관련 스타일은 없음 */
</style>
