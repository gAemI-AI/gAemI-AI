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

        if (msg.type === "chart_update") {
          const d = msg.data ?? msg;
          if (d.current_price != null) {
            this.ticks.push({
              price: d.current_price,
              rate: d.rate,
              timestamp: d.timestamp,
              volume: Number(d.tick_volume ?? 0),
            });
          }
          
          if (this.ticks.length > 200) this.ticks.shift();
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.socket = null;
        console.log("🔌 Chart WebSocket closed");
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
