import { defineStore } from "pinia";

/**
 * 🤖 AI Chatbot Store
 * - 챗봇 전역 상태 관리
 * - UI / 애니메이션 / 위치는 관여하지 않음
 * - 현재는 mock 기반, 추후 API 연동 예정
 */
export const useChatbotStore = defineStore("chatbot", {
  state: () => ({
    /** 챗봇 패널 열림 여부 */
    isOpen: false,

    /** 챗봇 메시지 목록 */
    messages: [],
  }),

  actions: {
    /** 챗봇 열기 */
    openChat() {
      this.isOpen = true;

      // ⭐ 처음 열릴 때만 초기 메시지 세팅
      if (this.messages.length === 0) {
        this.messages.push({
          role: "bot",
          content:
            '안녕하세요! "gAemI" AI 어시스턴트입니다.\n실시간 주가 데이터와 AI 뉴스 분석을 결합한 RAG 시스템으로 응답합니다.',
        });
      }
    },


    /** 챗봇 닫기 */
    closeChat() {
      this.isOpen = false;
    },

    /** 챗봇 열림/닫힘 토글 */
    toggleChat() {
      this.isOpen = !this.isOpen;
    },

    /**
     * 메시지 전송 (mock)
     * @param {string} text - 사용자 입력 메시지
     */
    sendMessageMock(text) {
      if (!text || !text.trim()) return;

      // 사용자 메시지
      this.messages.push({
        role: "user",
        content: text,
      });

      // mock AI 응답
      this.messages.push({
        role: "bot",
        content: "여기에 백엔드에서 받은 RAG 응답 내용을 표시합니다.",
      });
    },

    /** 대화 초기화 (선택) */
    clearMessages() {
      this.messages = [];
    },
  },
});
