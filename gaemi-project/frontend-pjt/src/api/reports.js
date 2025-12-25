import api from "@/api/axios";

/**
 * 내 관심 종목의 최신 주간 리포트 조회
 * GET /stocks/reports/weekly/
 */
export const fetchWeeklyReports = async () => {
  // Django View: WeeklyReportView (로그인 유저의 Watchlist 기준 필터링됨)
  const response = await api.get("/stocks/reports/weekly/");
  return response.data; 
};