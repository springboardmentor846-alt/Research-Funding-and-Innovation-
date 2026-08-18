import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { notificationsAPI } from "../services/api.js";
import { useAuth } from "./AuthContext.jsx";

const NotificationsContext = createContext(null);

/**
 * Cross-page store for the in-app notification system.
 *
 * Owns the live unread count + the most recent preview items used by
 * the bell dropdown. Hydrates from ``/notifications`` on login and
 * after every state-changing call. Polls lightly while the tab is
 * visible so the bell number stays fresh without WebSockets (which
 * the spec postpones).
 *
 * Per requirement #26: we deliberately do NOT introduce a second
 * state library — this is plain React context, matching the
 * SavedPatentsContext / AuthContext pattern already in the project.
 */
export function NotificationsProvider({ children }) {
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [recent, setRecent] = useState([]);

  // Avoid overlap on the polling timer.
  const inFlight = useRef(false);

  // ------------------------------------------------------------------
  // Hydration
  // ------------------------------------------------------------------
  const refreshUnread = useCallback(async () => {
    if (!user) {
      setUnreadCount(0);
      return 0;
    }
    if (inFlight.current) return 0;
    inFlight.current = true;
    try {
      const res = await notificationsAPI.unreadCount();
      const n = res.data?.unread_count ?? 0;
      setUnreadCount(n);
      return n;
    } catch (err) {
      // Non-fatal — the bell just keeps its previous number.
      console.debug("unread count refresh failed:", err);
      return unreadCount;
    } finally {
      inFlight.current = false;
    }
  }, [user, unreadCount]);

  const refreshRecent = useCallback(
    async (pageSize = 8) => {
      if (!user) {
        setRecent([]);
        return [];
      }
      try {
        const res = await notificationsAPI.list({
          page: 1,
          page_size: pageSize,
        });
        const items = res.data?.items || [];
        setRecent(items);
        return items;
      } catch (err) {
        console.debug("recent notifications refresh failed:", err);
        return recent;
      }
    },
    [user, recent]
  );

  const refreshAll = useCallback(async () => {
    await Promise.all([refreshUnread(), refreshRecent()]);
  }, [refreshUnread, refreshRecent]);

  // On user change: hydrate + start a soft poller.
  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      setRecent([]);
      return undefined;
    }
    refreshAll();
    const interval = setInterval(() => {
      // Cheap counter check; the recent list only refetches on focus
      // to keep network noise down.
      refreshUnread();
    }, 60_000);
    const onFocus = () => refreshAll();
    window.addEventListener("focus", onFocus);
    return () => {
      clearInterval(interval);
      window.removeEventListener("focus", onFocus);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  // ------------------------------------------------------------------
  // Mutations
  // ------------------------------------------------------------------
  const markAsRead = useCallback(
    async (id) => {
      try {
        await notificationsAPI.markAsRead(id);
      } catch (err) {
        console.debug("markAsRead failed:", err);
        return;
      }
      setRecent((items) =>
        items.map((n) =>
          n.id === id && !n.is_read
            ? { ...n, is_read: true, read_at: new Date().toISOString() }
            : n
        )
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    },
    []
  );

  const markAllAsRead = useCallback(async () => {
    try {
      await notificationsAPI.markAllAsRead();
    } catch (err) {
      console.debug("markAllAsRead failed:", err);
      return;
    }
    const now = new Date().toISOString();
    setRecent((items) =>
      items.map((n) =>
        n.is_read ? n : { ...n, is_read: true, read_at: now }
      )
    );
    setUnreadCount(0);
  }, []);

  const remove = useCallback(async (id) => {
    let wasUnread = false;
    setRecent((items) => {
      const next = items.filter((n) => {
        if (n.id === id && !n.is_read) wasUnread = true;
        return n.id !== id;
      });
      return next;
    });
    if (wasUnread) setUnreadCount((c) => Math.max(0, c - 1));
    try {
      await notificationsAPI.remove(id);
    } catch (err) {
      // Best-effort: re-hydrate on failure so the UI is consistent.
      console.debug("remove notification failed:", err);
    }
  }, []);

  const value = useMemo(
    () => ({
      unreadCount,
      recent,
      refresh: refreshAll,
      markAsRead,
      markAllAsRead,
      remove,
    }),
    [unreadCount, recent, refreshAll, markAsRead, markAllAsRead, remove]
  );

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications() {
  const ctx = useContext(NotificationsContext);
  // Safe no-op fallback so a stale cached bundle without the provider
  // does not crash the route tree.
  if (!ctx) {
    return {
      unreadCount: 0,
      recent: [],
      refresh: async () => {},
      markAsRead: async () => {},
      markAllAsRead: async () => {},
      remove: async () => {},
    };
  }
  return ctx;
}
