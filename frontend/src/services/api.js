import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Token refresh state
let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new Error("No refresh token");
  }
  const res = await axios.post(`${API_URL}/auth/refresh`, {
    refresh_token: refreshToken,
  });
  const { access_token, refresh_token } = res.data;
  localStorage.setItem("access_token", access_token);
  localStorage.setItem("refresh_token", refresh_token);
  return access_token;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/")
    ) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(originalRequest));
          });
        });
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        const newToken = await refreshAccessToken();
        isRefreshing = false;
        onTokenRefreshed(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        if (!window.location.pathname.startsWith("/login")) {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }
    if (error.response?.status === 401) {
      // Auth endpoint rejected - hard logout only if it wasn't a refresh attempt
      if (!originalRequest.url?.includes("/auth/refresh")) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        if (!window.location.pathname.startsWith("/login")) {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (payload) => api.post("/auth/register", payload),
  login: (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/auth/me"),
  updateMe: (payload) => api.put("/auth/me", payload),
  changePassword: (oldPassword, newPassword) =>
    api.post("/auth/change-password", { old_password: oldPassword, new_password: newPassword }),
  myStats: () => api.get("/auth/me/stats"),
  listUsers: (skip = 0, limit = 50) => api.get(`/auth/users?skip=${skip}&limit=${limit}`),
  changeUserRole: (userId, role) => api.put(`/auth/users/${userId}/role?role=${role}`),
  deactivateUser: (userId) => api.delete(`/auth/users/${userId}`),
  refreshToken: (refreshToken) => api.post("/auth/refresh", { refresh_token: refreshToken }),
};

// Publications
export const publicationsAPI = {
  list: (params) => api.get("/publications", { params }),
  listAll: (params) => api.get("/publications/all", { params }),
  get: (id) => api.get(`/publications/${id}`),
  create: (payload) => api.post("/publications", payload),
  update: (id, payload) => api.put(`/publications/${id}`, payload),
  delete: (id) => api.delete(`/publications/${id}`),
  stats: () => api.get("/publications/stats/me"),
};

// Funding — read-only for the public Funding page. Admin write actions
// (create / update / patch / delete) live in adminAPI and are routed to
// /admin/funding/* which is wired to FundingService. Keeping the public
// fundingAPI surface read-only avoids 404s on routes that no longer exist.
export const fundingAPI = {
  list: (params) => api.get("/funding", { params }),
  get: (id) => api.get(`/funding/${id}`),
  stats: () => api.get("/funding/stats/overview"),
  recommendations: (topK = 10) => api.get(`/funding/recommendations/me?top_k=${topK}`),
  // Force a recompute (manual refresh). Always runs the recommender and
  // replaces the cache for the current user.
  refreshRecommendations: (topK = 10) =>
    api.post(`/funding/recommendations/refresh?top_k=${topK}`),
};

// Dashboard
export const dashboardAPI = {
  overview: () => api.get("/dashboard/overview"),
  platform: () => api.get("/dashboard/platform"),
};

// Patents
export const patentsAPI = {
  search: (q, source = "all") => api.get(`/patents/search?q=${encodeURIComponent(q)}&source=${source}`),
  get: (id) => api.get(`/patents/${id}`),
  explain: (text) => api.post(`/patents/explain`, { patent_text: text }),
  analytics: () => api.get("/patents/analytics/overview"),
  gapAnalysis: () => api.get("/patents/gap-analysis/ai"),
};

// AI Assistant
export const aiAPI = {
  summarize: (text, max_length = 200, min_length = 60) =>
    api.post("/ai/summarize", { text, max_length, min_length }),
  explainPatent: (text) =>
    api.post("/ai/explain-patent", { text }),
  explainConcept: (concept) => api.post("/ai/explain-concept", { concept }),
  literatureReview: (topic) => api.post("/ai/literature-review", { topic }),
  commercialization: (abstract) => api.post("/ai/commercialization", { abstract }),
  researchDirections: (abstract) => api.post("/ai/research-directions", { abstract }),
};

// Trends
export const trendsAPI = {
  my: () => api.get("/trends/me"),
  emerging: () => api.get("/trends/emerging-topics"),
};

// Search
export const searchAPI = {
  publications: (q, page = 1, pageSize = 20) =>
    api.get(`/search/publications?q=${encodeURIComponent(q)}&page=${page}&page_size=${pageSize}`),
  funding: (q, page = 1, pageSize = 20) =>
    api.get(`/search/funding?q=${encodeURIComponent(q)}&page=${page}&page_size=${pageSize}`),
  semantic: (q, collection = "publications", topK = 10) =>
    api.post(`/search/semantic?q=${encodeURIComponent(q)}&collection=${collection}&top_k=${topK}`),
};

// Profile - Collaborations, Funding History, Research Interests
export const profileAPI = {
  listCollaborations: () => api.get("/profile/collaborations"),
  createCollaboration: (payload) => api.post("/profile/collaborations", payload),
  updateCollaboration: (id, payload) => api.put(`/profile/collaborations/${id}`, payload),
  deleteCollaboration: (id) => api.delete(`/profile/collaborations/${id}`),
  listFundingHistory: () => api.get("/profile/funding-history"),
  createFundingHistory: (payload) => api.post("/profile/funding-history", payload),
  updateFundingHistory: (id, payload) => api.put(`/profile/funding-history/${id}`, payload),
  deleteFundingHistory: (id) => api.delete(`/profile/funding-history/${id}`),
  // Research interests — tag-based, per-item CRUD plus a bulk replace.
  listResearchInterests: () => api.get("/profile/research-interests"),
  createResearchInterest: (payload) =>
    api.post("/profile/research-interests", payload),
  updateResearchInterest: (id, payload) =>
    api.put(`/profile/research-interests/${id}`, payload),
  deleteResearchInterest: (id) =>
    api.delete(`/profile/research-interests/${id}`),
  replaceResearchInterests: (items) =>
    api.put("/profile/research-interests", { items }),
  listResearchDomains: () => api.get("/profile/research-domains"),
};

// Admin Portal — wraps the /api/v1/admin/* endpoints.
// The admin never sees Apply buttons or researcher workflows.
export const adminAPI = {
  // Dashboard
  dashboardSummary: () => api.get("/admin/dashboard/summary"),
  recentActivity: (limit = 20) => api.get(`/admin/dashboard/recent-activity?limit=${limit}`),

  // Users
  listUsers: (params) => api.get("/admin/users", { params }),
  getUser: (id) => api.get(`/admin/users/${id}`),
  updateUser: (id, payload) => api.put(`/admin/users/${id}`, payload),
  activateUser: (id) => api.post(`/admin/users/${id}/activate`),
  deactivateUser: (id) => api.post(`/admin/users/${id}/deactivate`),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),

  // Funding — read-only legacy list. Sync controls live in fundingIntelAPI.
  listFunding: (params) => api.get("/admin/funding", { params }),
  fundingStats: () => api.get("/admin/funding/stats"),
  // Admin funding CRUD — used by the Funding Management page.
  createFunding: (payload) => api.post("/admin/funding", payload),
  updateFunding: (id, payload) => api.put(`/admin/funding/${id}`, payload),
  patchFunding: (id, payload) => api.patch(`/admin/funding/${id}`, payload),
  deleteFunding: (id) => api.delete(`/admin/funding/${id}`),

  // Publications monitoring
  listPublications: (params) => api.get("/publications/admin/all", { params }),
  publicationStats: () => api.get("/admin/publications/stats"),
  deletePublication: (id) => api.delete(`/admin/publications/${id}`),

  // Patents monitoring
  patentOverview: () => api.get("/admin/patents/overview"),

  // AI recommendations monitoring
  recommendationStats: () => api.get("/admin/recommendations/stats"),
  listRecommendations: (params) => api.get("/admin/recommendations", { params }),
  deleteRecommendation: (id) => api.delete(`/admin/recommendations/${id}`),
  regenerateRecommendations: (userId) =>
    api.post("/admin/recommendations/regenerate", { user_id: userId }),

  // Reports — CSV exports
  exportUsers: () => api.get("/admin/reports/users/export", { responseType: "blob" }),
  exportFunding: () => api.get("/admin/reports/funding/export", { responseType: "blob" }),
  exportPublications: () => api.get("/admin/reports/publications/export", { responseType: "blob" }),
  exportPatents: () => api.get("/admin/reports/patents/export", { responseType: "blob" }),

  // Settings
  getSettings: () => api.get("/admin/settings"),
  updateSettings: (payload) => api.put("/admin/settings", payload),
  addFundingCategory: (name) => api.post("/admin/settings/funding-categories", { name }),
  removeFundingCategory: (name) =>
    api.delete(`/admin/settings/funding-categories/${encodeURIComponent(name)}`),
  addResearchDomain: (name) => api.post("/admin/settings/research-domains", { name }),
  removeResearchDomain: (name) =>
    api.delete(`/admin/settings/research-domains/${encodeURIComponent(name)}`),
};

// Funding Intelligence — sync, health, observability.
export const fundingIntelAPI = {
  dashboard: () => api.get("/funding-intel/dashboard"),
  providers: () => api.get("/funding-intel/providers"),
  triggerSync: (payload = {}) => api.post("/funding-intel/sync", payload),
  pauseSync: () => api.post("/funding-intel/sync/pause"),
  resumeSync: () => api.post("/funding-intel/sync/resume"),
  logs: (params) => api.get("/funding-intel/logs", { params }),
  getLog: (runId) => api.get(`/funding-intel/logs/${runId}`),
  failedRecords: (params) => api.get("/funding-intel/failed-records", { params }),
  importedFunding: (params) => api.get("/funding-intel/funding", { params }),
  fundingStats: () => api.get("/funding-intel/funding/stats"),
};

export default api;

// ---------------------------------------------------------------------------
// Patent Intelligence — Milestone 3 endpoints (live corpus).
// Mounted under /api/v1/patents/intel/* in app.main.  Every value is
// computed by the backend services from the canonical ``patents`` table;
// the UI never sees mock data.
// ---------------------------------------------------------------------------
export const patentsIntelAPI = {
  // Patent Landscape Analysis
  landscape: () => api.get("/patents/intel/landscape"),

  // Technology Intelligence Engine
  clusters: () => api.get("/patents/intel/clusters"),
  emerging: () => api.get("/patents/intel/emerging"),
  fastGrowing: () => api.get("/patents/intel/fast-growing"),
  highlyCited: (limit = 10) =>
    api.get(`/patents/intel/highly-cited?limit=${limit}`),
  similar: (patentId, topK = 5) =>
    api.get(`/patents/intel/similar/${patentId}?top_k=${topK}`),

  // Innovation Scoring
  recomputeScores: () => api.post("/patents/intel/scores/recompute"),
  score: (patentId) => api.get(`/patents/intel/scores/${patentId}`),

  // Commercialization Recommendations
  recomputeRecommendations: () =>
    api.post("/patents/intel/recommendations/recompute"),
  recommendations: (limit = 10) =>
    api.get(`/patents/intel/recommendations?limit=${limit}`),

  // Patent Analytics Dashboard (cached, 5 min TTL)
  dashboard: (forceRefresh = false) =>
    api.get(`/patents/intel/dashboard?force_refresh=${forceRefresh}`),
  refreshDashboard: () => api.post("/patents/intel/dashboard/refresh"),

  // Sync controls (admin)
  syncStatus: () => api.get("/patents/intel/sync/status"),
  triggerSync: (payload = {}) => api.post("/patents/intel/sync", payload),
};

// ---------------------------------------------------------------------------
// Patent Intelligence Dashboard — per-patent AI insights.
//
// Mounted under /api/v1/patent-intel/* by backend.app.main.  All responses
// are powered by the existing OpenRouter AI service (app.services.ai_service)
// and the live patent corpus — no mock data.
// ---------------------------------------------------------------------------
export const patentDashboardAPI = {
  // 1. Patent Overview
  overview: (patentNumber) =>
    api.get(`/patent-intel/${encodeURIComponent(patentNumber)}/overview`),
  // 2. AI Patent Summary
  aiSummary: (patentNumber) =>
    api.get(`/patent-intel/${encodeURIComponent(patentNumber)}/ai-summary`),
  // 3. Innovation Scores (deterministic + optional AI verdict)
  innovationScores: (patentNumber, ai = false) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/innovation-scores?ai=${ai}`
    ),
  // 4. Tech Gap Analysis
  techGap: (patentNumber) =>
    api.get(`/patent-intel/${encodeURIComponent(patentNumber)}/tech-gap`),
  // 5. Commercial Applications
  commercialApplications: (patentNumber) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/commercial-applications`
    ),
  // 6. AI Recommendations
  recommendations: (patentNumber) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/recommendations`
    ),
  // 7. Related Funding
  relatedFunding: (patentNumber, topK = 8) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/related-funding?top_k=${topK}`
    ),
  // 8. Related Publications
  relatedPublications: (patentNumber, topK = 8) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/related-publications?top_k=${topK}`
    ),
  // 9. Similar Patents
  similarPatents: (patentNumber, topK = 8) =>
    api.get(
      `/patent-intel/${encodeURIComponent(patentNumber)}/similar-patents?top_k=${topK}`
    ),
  // 10. Technology Trend
  techTrend: (patentNumber) =>
    api.get(`/patent-intel/${encodeURIComponent(patentNumber)}/tech-trend`),
};

// Saved Patents — user-scoped bookmark library. Backend persists across
// sessions and is JWT-scoped, so each user only ever sees their own
// rows. Mirrors /api/v1/saved-patents/*.
export const savedPatentsAPI = {
  create: (payload) => api.post("/saved-patents", payload),
  list: (params) => api.get("/saved-patents", { params }),
  get: (id) => api.get(`/saved-patents/${id}`),
  remove: (id) => api.delete(`/saved-patents/${id}`),
  count: () => api.get("/saved-patents/count"),
};

// ---------------------------------------------------------------------------
// Notifications — user-scoped in-app alerts + alert preferences.
//
// Mirrors /api/v1/notifications/* and /api/v1/alert-preferences/*.
// The backend enforces ownership (every endpoint reads the JWT
// subject) so a user can never see or modify another user's rows.
// ---------------------------------------------------------------------------
export const notificationsAPI = {
  list: (params) => api.get("/notifications", { params }),
  unreadCount: () => api.get("/notifications/unread-count"),
  markAsRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllAsRead: () => api.patch("/notifications/read-all"),
  remove: (id) => api.delete(`/notifications/${id}`),
};

export const alertPreferencesAPI = {
  get: () => api.get("/alert-preferences"),
  update: (payload) => api.put("/alert-preferences", payload),
};
