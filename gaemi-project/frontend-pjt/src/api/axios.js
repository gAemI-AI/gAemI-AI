// src/api/axios.js
import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청마다 access token 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue = [];

const processQueue = (error, newAccessToken = null) => {
  refreshQueue.forEach((p) => {
    if (error) p.reject(error);
    else p.resolve(newAccessToken);
  });
  refreshQueue = [];
};

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    // 401 아니면 그대로 throw
    if (status !== 401) return Promise.reject(error);

    // refresh endpoint 자체에서 401이면 무한루프 방지
    if (originalRequest?.url?.includes("/users/token/refresh")) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    // 이미 재시도한 요청이면 종료 (무한루프 방지)
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    originalRequest._retry = true;

    const refreshToken = localStorage.getItem("refreshToken");
    if (!refreshToken) {
      // refresh 없으면 강제 로그아웃 처리
      localStorage.removeItem("accessToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    // 이미 refresh 중이면 큐에 쌓았다가 토큰 갱신 후 재시도
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({ resolve, reject });
      }).then((newToken) => {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      });
    }

    isRefreshing = true;

    try {
      // ⚠️ 여기 payload 키(refresh)가 맞는지 swagger로 확인
      const refreshRes = await api.post("/users/token/refresh/", {
        refresh: refreshToken,
      });

      // ⚠️ 여기 응답 키(access)가 맞는지 swagger로 확인
      const newAccessToken = refreshRes.data.access;

      localStorage.setItem("accessToken", newAccessToken);

      processQueue(null, newAccessToken);

      // 원래 요청 재시도
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    } catch (refreshErr) {
      processQueue(refreshErr, null);

      // refresh도 실패하면 로그아웃 처리
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
