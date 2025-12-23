import { defineStore } from "pinia";
import { useToastStore } from "@/stores/toastStore";

export const useNotificationSocketStore = defineStore("notificationSocket", {
  state: () => ({
    socket: null,
    isConnected: false,
  }),

  actions: {
    connect(userId) {
      if (this.socket) return;

      const toast = useToastStore();
      const url = `ws://localhost:8000/ws/notifications/${userId}/`;

      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log("✅ Notification WebSocket connected");
      };

      this.socket.onmessage = (event) => {
        let msg;
        try {
          msg = JSON.parse(event.data);
        } catch (e) {
          console.error("❌ WS JSON parse error", e);
          return;
        }

        if (msg.type === "alert") {
          toast.push({
            message: msg.data,
            type: "info",
          });
        }
      };

      this.socket.onerror = (err) => {
        console.error("❌ Notification WebSocket error", err);
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.socket = null;
        console.log("🔌 Notification WebSocket closed");
      };
    },

    disconnect() {
      this.socket?.close();
      this.socket = null;
      this.isConnected = false;
    },
  },
});
