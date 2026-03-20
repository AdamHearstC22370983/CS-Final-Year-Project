import axios from "axios";
import { clearCurrentUser, getAccessToken } from "./auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Attach the bearer token automatically to every request when present.
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// If the backend returns 401, clear the saved session.
// This protects the app from stale or expired tokens.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearCurrentUser();

      const currentPath = window.location.pathname;
      const isAuthPage = currentPath === "/login" || currentPath === "/register";

      if (!isAuthPage) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;