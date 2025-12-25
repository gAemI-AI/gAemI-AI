// src/api/notifications.js
import api from "./axios";

/**
 * 알림 규칙 목록 조회
 */
export const fetchNotificationRules = async () => {
  const res = await api.get("/notifications/rules/");
  return res.data;
};

/**
 * 알림 규칙 생성
 */
export const createNotificationRule = async (payload) => {
  const res = await api.post("/notifications/rules/", payload);
  return res.data;
};

/**
 * ✅ 알림 규칙 삭제 (중요)
 */
export const deleteNotificationRule = async (id) => {
  const res = await api.delete(`/notifications/rules/${id}/`);
  return res.data;
};