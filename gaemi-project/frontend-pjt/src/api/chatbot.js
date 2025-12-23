// src/api/chatbot.js
import api from "./axios"; // axios.js가 같은 폴더에 있다고 가정

/**
 * 챗봇에게 질문하기
 * POST /api/v1/chatbot/ask/
 * Body: { "question": "..." }
 */
export const askChatbot = async (question) => {
  // 백엔드 엔드포인트에 맞춰 수정 (/chatbot/ask/ 가 맞다고 가정)
  const response = await api.post("/chatbot/ask/", {
    question: question,
  });
  
  // 백엔드가 { "answer": "답변내용" } 형태로 준다고 가정하고 반환
  return response.data; 
};
