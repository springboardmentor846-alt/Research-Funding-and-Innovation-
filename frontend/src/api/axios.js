import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/*
  Request interceptor

  Runs before every API request.
  If a JWT exists, it automatically adds:

  Authorization: Bearer <token>
*/
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/*
  Response interceptor

  Runs after every API response.
  If the backend returns 401, the stored token is invalid
  or expired, so the user is logged out automatically.
*/
api.interceptors.response.use(
  (response) => response,

  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");

      const currentPath = window.location.pathname;

      const isPublicPage =
        currentPath === "/login" ||
        currentPath === "/register";

      if (!isPublicPage) {
        window.location.replace("/login");
      }
    }

    return Promise.reject(error);
  }
);

export default api;