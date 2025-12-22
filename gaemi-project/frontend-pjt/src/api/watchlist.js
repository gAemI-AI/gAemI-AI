// src/api/watchlist.js
import api from "./axios";

/**
 * 관심종목 목록 조회
 * GET /watchlist/
 */
export const getWatchlist = async () => {
  const res = await api.get("/watchlist/");
  return res.data;
};

/**
 * 관심종목 추가
 * POST /watchlist/
 * @param {string} stockCode - 종목 ID
 */
export const addWatchlist = async (stockCode) => {
  const res = await api.post("/watchlist/", {
    stock: stockCode,
  });
  return res.data;
};

/**
 * 관심종목 삭제
 * DELETE /watchlist/{stock_id}/
 * @param {string} stockCode - 종목 ID
 */
export const removeWatchlist = async (stockCode) => {
  const res = await api.delete(`/watchlist/${stockCode}/`);
  return res.data;
};
