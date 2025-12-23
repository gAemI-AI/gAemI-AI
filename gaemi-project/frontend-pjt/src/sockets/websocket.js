export function createWebSocket(url, { onOpen, onMessage, onError }) {
  const socket = new WebSocket(url);

  socket.onopen = () => {
    console.log(`✅ WebSocket connected: ${url}`);
    onOpen?.();
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (e) {
      console.error("❌ WebSocket JSON parse error", e);
    }
  };

  socket.onerror = (error) => {
    console.error("❌ WebSocket error", error);
    onError?.(error);
  };

  return socket;
}
