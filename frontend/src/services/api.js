import axios from "axios";

const BASE_URL = "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const loginUser = (email, password) => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return api.post("/auth/login", form);
};
export const registerUser = (data) => api.post("/auth/register", data);

// Profile
export const getMyProfile = () => api.get("/profile/me");
export const createProfile = (data) => api.post("/profile/", data);
export const updateProfile = (data) => api.put("/profile/", data);

// Funding
export const getFunding = (params) => api.get("/funding/", { params });
export const getFundingById = (id) => api.get(`/funding/${id}`);
export const createFunding = (data) => api.post("/funding/", data);
export const updateFunding = (id, data) => api.put(`/funding/${id}`, data);
export const deleteFunding = (id) => api.delete(`/funding/${id}`);

// Recommendations
export const getRecommendations = (userId) => api.get(`/recommendations/${userId}`);
export const checkEligibility = (fundingId) => api.get(`/recommendations/eligibility/${fundingId}`);

// Publications
export const getPublications = (params) => api.get("/publications/", { params });
export const getPublicationTrends = () => api.get("/publications/trends");
export const getDomainAnalysis = () => api.get("/publications/domain-analysis");
export const getYearAnalysis = () => api.get("/publications/year-analysis");
export const getTopKeywords = () => api.get("/publications/keywords");

// Dashboard
export const getDashboardStats = () => api.get("/dashboard/stats");

export default api;
