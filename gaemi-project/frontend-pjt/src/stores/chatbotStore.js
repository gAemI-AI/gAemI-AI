import { defineStore } from "pinia";
import { askChatbot } from "@/api/chatbot";

const STORAGE_KEYS = {
  OPEN: "chatbot_open",
  MESSAGES: "chatbot_messages",
};

export const useChatbotStore = defineStore("chatbot", {
  state: () => ({
    isOpen: localStorage.getItem(STORAGE_KEYS.OPEN) === 'true',
    messages: [],
    isLoading: false,
    lastError: null,
  }),

  getters: {
    hasMessages: (state) => state.messages.length > 0,
    lastMessage: (state) =>
      state.messages.length ? state.messages[state.messages.length - 1] : null,
  },

  actions: {
    init() {
      this.loadFromLocal();
      // 열려있는데 메시지가 하나도 없으면 안내 메시지 추가
      if (this.isOpen && this.messages.length === 0) {
        this.addSystemMessage("안녕하세요 👋\n관심 종목, 실적, 뉴스 요약 등 무엇이든 물어보세요.");
      }
    },

    open() {
      this.isOpen = true;
      localStorage.setItem(STORAGE_KEYS.OPEN, "true");
      if (this.messages.length === 0) {
        this.addSystemMessage("안녕하세요 👋\n관심 종목, 실적, 뉴스 요약 등 무엇이든 물어보세요.");
      }
    },

    close() {
      this.isOpen = false;
      localStorage.setItem(STORAGE_KEYS.OPEN, "false");
    },

    toggle() {
      this.isOpen ? this.close() : this.open();
    },

    /* -----------------------
       메시지 조작
    ------------------------ */
    addMessage(role, content, meta = {}) {
      if (!content && role !== 'system') return;

      this.messages.push({
        id: Date.now() + Math.random(),
        role,
        content,
        createdAt: new Date().toISOString(),
        references: meta.references || [],
      });
      this.saveToLocal();
    },

    addSystemMessage(text) { this.addMessage("system", text); },
    addUserMessage(text) { this.addMessage("user", text); },
    addAssistantMessage(text, references = []) { 
      this.addMessage("assistant", text, { references }); 
    },

    /* --------------------------------------------------
       ✅ [핵심] 로그아웃 시 호출될 초기화 함수
       - 메모리(state)와 로컬스토리지 모두 삭제
    -------------------------------------------------- */
    clearMessages() {
      this.messages = []; // 화면에서 즉시 삭제
      this.isOpen = false; // 챗봇 패널도 닫기
      
      // 로컬 스토리지 삭제
      localStorage.removeItem(STORAGE_KEYS.MESSAGES);
      localStorage.setItem(STORAGE_KEYS.OPEN, "false");
      
      this.lastError = null;
      this.isLoading = false;
    },

    /* -----------------------
       API 통신
    ------------------------ */
    async send(text) {
      const userText = (text ?? "").toString().trim();
      if (!userText) return;

      this.addUserMessage(userText);
      this.isLoading = true;
      this.lastError = null;

      try {
        const response = await askChatbot(userText);
        
        const answer = response.answer || response.data?.answer || "답변을 불러올 수 없습니다.";
        const refs = response.references || response.data?.references || [];

        this.addAssistantMessage(answer, refs);

      } catch (err) {
        console.error("Chatbot Error:", err);
        this.lastError = err;
        this.addSystemMessage("오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      } finally {
        this.isLoading = false;
      }
    },

    loadFromLocal() {
      const saved = localStorage.getItem(STORAGE_KEYS.MESSAGES);
      if (saved) {
        try { this.messages = JSON.parse(saved); } catch (e) {}
      }
    },
    
    saveToLocal() {
      localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(this.messages));
    }
  },
});