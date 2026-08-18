import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authAPI } from "../services/api.js";
import { clearAllDashboardCaches } from "../utils/dashboardCache.js";
import { clearAllPatentCaches } from "../utils/patentAIcache.js";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const stored = localStorage.getItem("user");
    if (token && stored) {
      try {
        setUser(JSON.parse(stored));
        // Refresh user info in the background
        authAPI
          .me()
          .then((res) => {
            setUser(res.data);
            localStorage.setItem("user", JSON.stringify(res.data));
          })
          .catch(() => logout())
          .finally(() => setLoading(false));
      } catch {
        logout();
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  async function login(username, password) {
    const res = await authAPI.login(username, password);
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    const me = await authAPI.me();
    setUser(me.data);
    localStorage.setItem("user", JSON.stringify(me.data));
    return me.data;
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    // Drop any session-tab dashboard cache so the next login does not
    // briefly paint the previous researcher's numbers.
    clearAllDashboardCaches();
    // Drop any per-patent AI dashboard cache so the next login does not
    // see the previous researcher's cached AI summaries.
    clearAllPatentCaches();
    setUser(null);
  }

  async function register(payload) {
    await authAPI.register(payload);
    return login(payload.username, payload.password);
  }

  // Refresh the current user (called after profile updates)
  const refreshUser = useCallback(async () => {
    try {
      const me = await authAPI.me();
      setUser(me.data);
      localStorage.setItem("user", JSON.stringify(me.data));
      return me.data;
    } catch (err) {
      console.error("Failed to refresh user:", err);
      return null;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
