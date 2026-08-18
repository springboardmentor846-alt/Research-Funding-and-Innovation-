import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { savedPatentsAPI } from "../services/api.js";
import { useAuth } from "./AuthContext.jsx";

const SavedPatentsContext = createContext(null);

/**
 * Cross-page store for "saved patents" — owns the live count and the
 * set of `${source}::${patent_number}` keys the user currently has
 * bookmarked. Both pieces of state are server-authoritative; we
 * hydrate on login and revalidate after every create / remove.
 */
export function SavedPatentsProvider({ children }) {
  const { user } = useAuth();
  const [count, setCount] = useState(0);
  const [keys, setKeys] = useState(() => new Set());

  const refresh = useCallback(async () => {
    if (!user) {
      setCount(0);
      setKeys(new Set());
      return;
    }
    try {
      // Pull the count + first page of saved patents in parallel so the
      // dashboard KPI and isSaved() lookups hydrate together.
      const [countRes, listRes] = await Promise.all([
        savedPatentsAPI.count(),
        savedPatentsAPI.list({ page: 1, page_size: 100 }),
      ]);
      setCount(countRes.data?.count ?? 0);
      const next = new Set();
      for (const item of listRes.data?.items || []) {
        next.add(`${item.source || ""}::${item.patent_number || ""}`);
      }
      setKeys(next);
    } catch (err) {
      // Silent: the saved-patents KPI is decorative. Network errors
      // surface elsewhere via the calling component.
      console.debug("SavedPatents refresh failed:", err);
    }
  }, [user]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const isSaved = useCallback(
    (patentNumber, source) =>
      keys.has(`${source || ""}::${patentNumber || ""}`),
    [keys]
  );

  const addLocal = useCallback((saved) => {
    if (!saved) return;
    const k = `${saved.source || ""}::${saved.patent_number || ""}`;
    setKeys((prev) => {
      if (prev.has(k)) return prev;
      const next = new Set(prev);
      next.add(k);
      return next;
    });
    setCount((c) => c + 1);
  }, []);

  const removeLocal = useCallback((savedId, fallback) => {
    if (fallback?.patent_number && fallback?.source) {
      const k = `${fallback.source}::${fallback.patent_number}`;
      setKeys((prev) => {
        if (!prev.has(k)) return prev;
        const next = new Set(prev);
        next.delete(k);
        return next;
      });
    }
    setCount((c) => Math.max(0, c - 1));
  }, []);

  const value = useMemo(
    () => ({ count, isSaved, refresh, addLocal, removeLocal }),
    [count, isSaved, refresh, addLocal, removeLocal]
  );

  return (
    <SavedPatentsContext.Provider value={value}>
      {children}
    </SavedPatentsContext.Provider>
  );
}

export function useSavedPatents() {
  const ctx = useContext(SavedPatentsContext);
  // Return safe no-op defaults when the provider is not present so a
  // single missing wrap (e.g. on a stale cached bundle) cannot crash
  // the entire route tree — the buttons degrade to "Save Patent" /
  // "★ Saved" purely based on optimistic local state, which the page
  // already handles.
  if (!ctx) {
    return {
      count: 0,
      isSaved: () => false,
      refresh: async () => {},
      addLocal: () => {},
      removeLocal: () => {},
    };
  }
  return ctx;
}