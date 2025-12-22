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
 * @param {string|number} stockId - 종목 ID
 */
export const addWatchlist = async (stockId) => {
  const res = await api.post("/watchlist/", {
    stock_id: stockId,
  });
  return res.data;
};

/**
 * 관심종목 삭제
 * DELETE /watchlist/{stock_id}/
 * @param {string|number} stockId - 종목 ID
 */
export const removeWatchlist = async (stockId) => {
  const res = await api.delete(`/watchlist/${stockId}/`);
  return res.data;
};
