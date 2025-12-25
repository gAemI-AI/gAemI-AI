import { defineStore } from "pinia";

let id = 0;

export const useToastStore = defineStore("toast", {
  state: () => ({
    toasts: [],
    max: 5, // ⭐ 최대 5개
  }),

  actions: {
    add(toast) {
      const newToast = {
        id: id++,
        type: toast.type || "info",
        title: toast.title || "",
        message: toast.message || "",
        duration: toast.duration || 3000, // 기본값 3초
        ...toast,
      };

      this.toasts.push(newToast);

      // ⭐ FIFO: 5개 초과 시 앞에서 제거
      if (this.toasts.length > this.max) {
        this.toasts.shift();
      }

      return newToast.id;
    },

    push(toast) {
      return this.add(toast);
    },

    remove(toastId) {
      this.toasts = this.toasts.filter((t) => t.id !== toastId);
    },
  },
});
