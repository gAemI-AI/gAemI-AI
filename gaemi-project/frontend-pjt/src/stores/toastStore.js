import { defineStore } from "pinia";

let id = 0;

export const useToastStore = defineStore("toast", {
  state: () => ({
    toasts: [],
    max: 5, // ⭐ 최대 5개
  }),

  actions: {
    push(toast) {
      this.toasts.push({
        id: id++,
        ...toast,
      });

      // ⭐ FIFO: 5개 초과 시 앞에서 제거
      if (this.toasts.length > this.max) {
        this.toasts.shift();
      }
    },

    remove(toastId) {
      this.toasts = this.toasts.filter((t) => t.id !== toastId);
    },
  },
});
