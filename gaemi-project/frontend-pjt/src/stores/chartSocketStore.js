import { defineStore } from "pinia";

export const useChartSocketStore = defineStore("chartSocket", {
  state: () => ({
    socket: null,
    code: null,
    isConnected: false,
    ticks: [],
  }),

  actions: {
    connect(stockCode) {
      if (this.socket && this.code === stockCode) return;

      this.disconnect();

      this.code = stockCode;
      this.ticks = [];

      const url = `ws://localhost:8000/ws/stocks/${stockCode}/`;
      console.log("📈 Chart WS connect:", url);

      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log("✅ Chart WebSocket connected");
      };

      this.socket.onmessage = (event) => {
        console.log("📩 chart ws raw:", event.data);
        let msg;
        try {
          msg = JSON.parse(event.data);
        } catch {
          return;
        }

        if (msg?.type !== "chart_update") return;
        
        const d = msg.data ?? msg;

        const price = Number(d.price ?? d.current_price);
        const rate = Number(d.rate ?? 0);
        const timestamp = Number(d.timestamp ?? Date.now());
        const volume = Number(d.volume ?? d.tick_volume ?? d.v ?? 0);
        
        if (!Number.isFinite(price)) return;

        this.ticks.push({ price, rate, timestamp, volume });
        if (this.ticks.length > 200) this.ticks.shift();
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.socket = null;
        console.log("🔌 Chart WebSocket closed");
      };

      this.socket.onerror = (e) => {
        console.log("❌ Chart WebSocket error:", e);
      };
    },

    disconnect() {
      if (this.socket) this.socket.close();
      this.socket = null;
      this.code = null;
      this.isConnected = false;
      this.ticks = [];
    },
  },
});
