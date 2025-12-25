/**
 * WebSocket 서비스
 * 실시간 주식 데이터 및 알림을 WebSocket으로 받음
 */

const WS_BASE_URL = 'ws://localhost:8000';

class WebSocketService {
  constructor() {
    this.sockets = new Map(); // 연결 유지
    this.listeners = new Map(); // 이벤트 리스너
  }

  /**
   * 주식 실시간 데이터 구독 (차트 업데이트용)
   * @param {string} stockCode - 종목 코드 (예: 005930)
   * @param {function} callback - 메시지 수신 콜백
   * @returns {function} 언서브스크라이브 함수
   */
  subscribeStock(stockCode, callback) {
    const url = `${WS_BASE_URL}/ws/stocks/${stockCode}/`;
    
    if (this.sockets.has(stockCode)) {
      const socket = this.sockets.get(stockCode);
      if (!this.listeners.has(stockCode)) {
        this.listeners.set(stockCode, []);
      }
      this.listeners.get(stockCode).push(callback);
      return () => this.unsubscribeStock(stockCode, callback);
    }

    return new Promise((resolve, reject) => {
      try {
        const socket = new WebSocket(url);

        socket.onopen = () => {
          console.log(`[${stockCode}] WebSocket 연결 성공`);
          this.sockets.set(stockCode, socket);
          
          if (!this.listeners.has(stockCode)) {
            this.listeners.set(stockCode, []);
          }
          this.listeners.get(stockCode).push(callback);

          // 언서브스크라이브 함수 반환
          resolve(() => this.unsubscribeStock(stockCode, callback));
        };

        socket.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            console.log(`[WebSocket ${stockCode}] 메시지 수신:`, response);
            
            // 모든 등록된 리스너에 전달
            const cbs = this.listeners.get(stockCode) || [];
            cbs.forEach(cb => {
              try {
                cb(response);
              } catch (err) {
                console.error(`콜백 실행 중 에러:`, err);
              }
            });
          } catch (err) {
            console.error(`메시지 파싱 에러:`, err);
          }
        };

        socket.onerror = (error) => {
          console.error(`[${stockCode}] WebSocket 에러:`, error);
          reject(error);
        };

        socket.onclose = () => {
          console.log(`[${stockCode}] WebSocket 연결 종료`);
          this.sockets.delete(stockCode);
          this.listeners.delete(stockCode);
        };
      } catch (err) {
        console.error(`WebSocket 생성 에러:`, err);
        reject(err);
      }
    });
  }

  /**
   * 주식 구독 해제
   * @param {string} stockCode - 종목 코드
   * @param {function} callback - 해제할 콜백
   */
  unsubscribeStock(stockCode, callback) {
    const cbs = this.listeners.get(stockCode) || [];
    const index = cbs.indexOf(callback);
    
    if (index > -1) {
      cbs.splice(index, 1);
    }

    // 리스너가 없으면 소켓 종료
    if (cbs.length === 0) {
      const socket = this.sockets.get(stockCode);
      if (socket) {
        socket.close();
        this.sockets.delete(stockCode);
        this.listeners.delete(stockCode);
      }
    }
  }

  /**
   * 개인 알림 구독
   * @param {string} userId - 사용자 ID
   * @param {function} callback - 메시지 수신 콜백
   * @returns {function} 언서브스크라이브 함수
   */
  subscribeNotifications(userId, callback) {
    const key = `notifications_${userId}`;
    const url = `${WS_BASE_URL}/ws/notifications/${userId}/`;

    if (this.sockets.has(key)) {
      const socket = this.sockets.get(key);
      if (!this.listeners.has(key)) {
        this.listeners.set(key, []);
      }
      this.listeners.get(key).push(callback);
      return () => this.unsubscribeNotifications(userId, callback);
    }

    return new Promise((resolve, reject) => {
      try {
        const socket = new WebSocket(url);

        socket.onopen = () => {
          console.log(`[Notifications ${userId}] WebSocket 연결 성공`);
          this.sockets.set(key, socket);
          
          if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
          }
          this.listeners.get(key).push(callback);

          resolve(() => this.unsubscribeNotifications(userId, callback));
        };

        socket.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            console.log(`[WebSocket Notifications ${userId}] 메시지 수신:`, response);
            const cbs = this.listeners.get(key) || [];
            cbs.forEach(cb => {
              try {
                cb(response);
              } catch (err) {
                console.error(`콜백 실행 중 에러:`, err);
              }
            });
          } catch (err) {
            console.error(`메시지 파싱 에러:`, err);
          }
        };

        socket.onerror = (error) => {
          console.error(`[Notifications ${userId}] WebSocket 에러:`, error);
          reject(error);
        };

        socket.onclose = () => {
          console.log(`[Notifications ${userId}] WebSocket 연결 종료`);
          this.sockets.delete(key);
          this.listeners.delete(key);
        };
      } catch (err) {
        console.error(`WebSocket 생성 에러:`, err);
        reject(err);
      }
    });
  }

  /**
   * 알림 구독 해제
   * @param {string} userId - 사용자 ID
   * @param {function} callback - 해제할 콜백
   */
  unsubscribeNotifications(userId, callback) {
    const key = `notifications_${userId}`;
    const cbs = this.listeners.get(key) || [];
    const index = cbs.indexOf(callback);
    
    if (index > -1) {
      cbs.splice(index, 1);
    }

    if (cbs.length === 0) {
      const socket = this.sockets.get(key);
      if (socket) {
        socket.close();
        this.sockets.delete(key);
        this.listeners.delete(key);
      }
    }
  }

  /**
   * 모든 연결 종료
   */
  closeAll() {
    this.sockets.forEach((socket, key) => {
      socket.close();
    });
    this.sockets.clear();
    this.listeners.clear();
  }
}

export default new WebSocketService();
