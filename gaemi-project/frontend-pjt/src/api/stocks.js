// src/api/stocks.js
import api from "@/api/axios"; // ✅ axios 대신 api로 이름 변경

export const fetchStockMaster = async () => {
  const res = await api.get("/stocks/");
  return res.data;
};

export const getStockChart = (stockCode) => {
  return api.get(`stocks/${stockCode}/chart/`); // ✅ 여기도 api로 통일
};

/**
 * 특정 종목의 AI 뉴스 요약 조회
 * GET /news/{stock_code}/
 */
export const fetchStockNews = async (stockCode) => {
  const response = await api.get(`/news/${stockCode}/`);
  return response.data; 
};
