// src/stores/chatbotStore.js
import { defineStore } from "pinia";

export const useChatbotStore = defineStore("chatbot", {
  state: () => ({
    // 우측 하단 패널 열림/닫힘
    isOpen: false,

    // ✅ 우측 하단 챗봇 + ChatbotPage가 "같이" 쓰는 대화 기록
    // role: "user" | "assistant" | "system"
    // content: string
    messages: [],

    // 입력/응답 진행 상태 (UI에서 스피너 등)
    isLoading: false,

    // 필요하면 에러 표시
    lastError: null,
  }),

  getters: {
    hasMessages: (state) => state.messages.length > 0,
    lastMessage: (state) =>
      state.messages.length ? state.messages[state.messages.length - 1] : null,
  },

  actions: {
    /* -----------------------
       Panel/Page 공통 제어
    ------------------------ */
    open() {
      this.isOpen = true;

      // ✅ 처음 열릴 때만 안내 메시지 추가
      if (this.messages.length === 0) {
        this.addSystemMessage(
          "안녕하세요 👋\n관심 종목, 실적, 뉴스 요약 등 무엇이든 물어보세요."
        );
      }
    },
    close() {
      this.isOpen = false;
    },
    toggle() {
      this.isOpen = !this.isOpen;
    },

    /* -----------------------
       메시지 조작 (공통)
    ------------------------ */
    addMessage(role, content, meta = {}) {
      // content가 비어있으면 추가하지 않음(실수 방지)
      const text = (content ?? "").toString();
      if (!text.trim()) return;

      this.messages.push({
        id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
        role,
        content: text,
        createdAt: new Date().toISOString(),
        ...meta,
      });
    },

    addUserMessage(text, meta) {
      this.addMessage("user", text, meta);
    },

    addAssistantMessage(text, meta) {
      this.addMessage("assistant", text, meta);
    },

    addSystemMessage(text, meta) {
      this.addMessage("system", text, meta);
    },

    clearMessages() {
      this.messages = [];
      this.lastError = null;
      this.isLoading = false;
    },

    /* -----------------------
       (선택) 로컬스토리지 영속화
       - 새로고침해도 대화 유지하고 싶으면 사용
       - 원치 않으면 이 블록 통째로 안 써도 됨
    ------------------------ */
    loadFromLocal() {
      try {
        const raw = localStorage.getItem("chatbot_messages");
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) this.messages = parsed;
      } catch (e) {
        // 파싱 실패 시 무시
      }
    },

    saveToLocal() {
      try {
        localStorage.setItem("chatbot_messages", JSON.stringify(this.messages));
      } catch (e) {
        // 저장 실패 시 무시
      }
    },

    /* -----------------------
       (선택) 통합 send 액션
       - 지금은 mock 응답으로 둠
       - 나중에 API 붙일 때 여기만 교체하면 됨
    ------------------------ */
    async send(text) {
      const userText = (text ?? "").toString().trim();
      if (!userText) return;

      this.lastError = null;
      this.isLoading = true;

      // 1) 사용자 메시지 기록
      this.addUserMessage(userText);

      try {
        // ✅ TODO: 실제 백엔드/LLM API 호출로 교체
        // const res = await api.post("/chat", { message: userText });
        // this.addAssistantMessage(res.data.answer);

        // 임시 mock 응답
        await new Promise((r) => setTimeout(r, 250));
        this.addAssistantMessage(`(임시응답) "${userText}"에 대한 답변입니다.`);

        // 저장(원하면)
        this.saveToLocal();
      } catch (e) {
        this.lastError = "챗봇 응답에 실패했습니다.";
      } finally {
        this.isLoading = false;
      }
    },
  },
});
