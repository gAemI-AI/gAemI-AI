// src/api/notifications.js
import api from "./axios";

/**
 * 알림 규칙 목록 조회
 * GET /notifications/rules/
 */
export const fetchNotificationRules = async () => {
  const res = await api.get("/notifications/rules/");
  return res.data;
};

/**
 * 알림 규칙 생성
 * POST /notifications/rules/
 */
export const createNotificationRule = async (payload) => {
  const res = await api.post("/notifications/rules/", payload);
  return res.data;
};

/**
 * 알림 규칙 삭제
 * DELETE /notifications/rules/{rule_id}/
 */
export const deleteNotificationRule = async (ruleId) => {
  await api.delete(`/notifications/rules/${ruleId}/`);
};
