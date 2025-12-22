import axios from "@/api/axios"; // 이미 쓰고 있는 axios 인스턴스

export const getStockChart = (stockCode) => {
  return axios.get(`/api/v1/stocks/${stockCode}/chart/`);
};
