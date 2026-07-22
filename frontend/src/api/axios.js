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

  async (error) => {

    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {

      originalRequest._retry = true;

      const refreshToken =
        localStorage.getItem("refresh_token");

      if (!refreshToken) {

        localStorage.removeItem("access_token");

        window.location.replace("/login");

        return Promise.reject(error);

      }

      try {

        const response = await axios.post(
          "http://127.0.0.1:8000/auth/refresh",
          {
            refresh_token: refreshToken,
          }
        );

        const newAccessToken =
          response.data.access_token;

        localStorage.setItem(
          "access_token",
          newAccessToken
        );

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`;

        return api(originalRequest);

      }

      catch {

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        window.location.replace("/login");

      }

    }

    return Promise.reject(error);

  }

);

export default api;