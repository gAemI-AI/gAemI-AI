<template>
  <div class="toast" :class="type">
    <div class="icon">
      <span v-if="type === 'warning'">⚠️</span>
      <span v-else-if="type === 'success'">✅</span>
      <span v-else>ℹ️</span>
    </div>
    <div class="body">
      <div class="title">{{ title }}</div>
      <div class="msg">{{ message }}</div>
      <div class="time">오전 10:36</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'info' },
  title: { type: String, required: true },
  message: { type: String, required: true },
});
</script>

<style scoped>
.toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 320px;
  padding: 14px 16px;
  border-radius: 14px;
  background: white;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  display: flex;
  gap: 10px;
  z-index: 40;
  border-left: 4px solid #2563eb;
}
.toast.warning {
  border-color: #f97316;
}
.toast.success {
  border-color: #16a34a;
}
.icon {
  font-size: 20px;
}
.body {
  flex: 1;
}
.title {
  font-weight: 600;
  margin-bottom: 4px;
}
.msg {
  font-size: 13px;
}
.time {
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}
</style>
