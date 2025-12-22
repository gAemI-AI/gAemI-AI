// src/api/chatbot.js
import api from "./axios";

/**
 * Chatbot 질문 요청
 * @param {string} question - 사용자 질문
 * @returns {Promise<{ answer: string }>} 챗봇 응답
 */
export const askChatbot = async (question) => {
  const res = await api.post("/chatbot/ask/", {
    question,
  });
  return res.data;
};
