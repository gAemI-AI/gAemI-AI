import axios from "@/api/axios"; // 이미 쓰고 있는 axios 인스턴스

export const fetchStockMaster = async () => {
  const res = await api.get("/stocks/");
  return res.data;
};

export const getStockChart = (stockCode) => {
  return axios.get(`stocks/${stockCode}/chart/`);
};
