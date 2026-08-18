import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../context/NotificationsContext.jsx";
import { notificationsAPI } from "../services/api.js";

/**
 * Dedicated notifications page.
 *
 * - Tabbed filters: All | Unread | Funding | Patents | Research | System.
 * - Paginated server-side (page_size = 20).
 * - Each row supports: mark-as-read, delete, click-to-navigate.
 * - Priority is communicated via a coloured left border + chip.
 *
 * Per requirement #20: matches the existing card / tailwind patterns
 * of Dashboard / Funding / etc.  No new UI library is pulled in.
 */
export default function Notifications() {
  const { refresh, markAsRead, markAllAsRead, remove } = useNotifications();
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);

  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("all");
  const [error, setError] = useState("");

  const tabs = [
    { key: "all", label: "All" },
    { key: "unread", label: "Unread" },
    { key: "FUNDING_NEW", label: "Funding" },
    { key: "PATENT", label: "Patents" },
    { key: "RESEARCH_TREND", label: "Research" },
    { key: "RECOMMENDATION", label: "Recs" },
    { key: "SYSTEM", label: "System" },
  ];

  const load = useCallback(
    async (nextPage = page) => {
      setLoading(true);
      setError("");
      try {
        const params = { page: nextPage, page_size: pageSize };
        if (tab === "unread") {
          params.only_unread = true;
        } else if (tab !== "all") {
          params.notification_type = tab;
        }
        const res = await notificationsAPI.list(params);
        const data = res.data || {};
        setItems(data.items || []);
        setTotal(data.total || 0);
        setPage(data.page || 1);
        setTotalPages(data.total_pages || 0);
        setUnreadCount(data.unread_count || 0);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load notifications");
      } finally {
        setLoading(false);
      }
    },
    [page, pageSize, tab]
  );

  useEffect(() => {
    setPage(1);
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  useEffect(() => {
    load(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  async function handleSelect(n) {
    if (!n.is_read) await markAsRead(n.id);
    if (n.action_url) navigate(n.action_url);
  }

  async function handleDelete(id) {
    if (!window.confirm("Dismiss this notification?")) return;
    await remove(id);
    await refresh();
    load(page);
  }

  async function handleMarkAll() {
    await markAllAsRead();
    await load(page);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🔔 Notifications</h1>
          <div className="text-sm text-slate-500">
            {unreadCount > 0
              ? `${unreadCount} unread · ${total} total`
              : `${total} total`}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="btn-secondary text-sm"
            onClick={handleMarkAll}
            disabled={unreadCount === 0}
          >
            Mark all as read
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="card p-0">
        <div className="flex flex-wrap border-b border-slate-200">
          {tabs.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={`px-4 py-3 text-sm font-medium border-b-2 -mb-px transition ${
                tab === t.key
                  ? "border-primary-600 text-primary-700"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-700 text-sm">{error}</div>
        )}

        {loading ? (
          <div className="p-10 text-center text-slate-500">Loading…</div>
        ) : items.length === 0 ? (
          <div className="p-10 text-center text-slate-500">
            No notifications in this view yet.
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {items.map((n) => (
              <li
                key={n.id}
                className={`p-4 flex items-start gap-3 ${n.is_read ? "" : "bg-primary-50/30"}`}
              >
                <PriorityStripe priority={n.priority} />
                <div className="flex-1 min-w-0">
                  <button
                    type="button"
                    onClick={() => handleSelect(n)}
                    className="w-full text-left"
                  >
                    <div className="flex items-center gap-2 flex-wrap">
                      <div
                        className={`text-sm font-semibold ${
                          n.is_read ? "text-slate-600" : "text-slate-800"
                        }`}
                      >
                        {n.title}
                      </div>
                      <TypeChip type={n.notification_type} />
                      {!n.is_read && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-primary-100 text-primary-700 font-medium">
                          New
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-slate-600 mt-1 whitespace-pre-line">
                      {n.message}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      {new Date(n.created_at).toLocaleString()}
                    </div>
                  </button>
                </div>
                <div className="flex flex-col gap-1 flex-shrink-0">
                  {!n.is_read && (
                    <button
                      type="button"
                      onClick={() => markAsRead(n.id)}
                      className="btn-ghost text-xs"
                    >
                      Mark read
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => handleDelete(n.id)}
                    className="btn-ghost text-xs text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 text-sm">
            <div className="text-slate-500">
              Page {page} of {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-secondary text-xs"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="btn-secondary text-xs"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function PriorityStripe({ priority }) {
  const cls =
    priority === "CRITICAL"
      ? "bg-red-500"
      : priority === "HIGH"
      ? "bg-amber-500"
      : priority === "LOW"
      ? "bg-slate-300"
      : "bg-primary-500";
  return <div className={`w-1 self-stretch rounded-full ${cls}`} />;
}

function TypeChip({ type }) {
  const map = {
    FUNDING_NEW: { label: "Funding", cls: "bg-emerald-100 text-emerald-700" },
    FUNDING_MATCH: { label: "Match", cls: "bg-emerald-100 text-emerald-700" },
    FUNDING_DEADLINE: { label: "Deadline", cls: "bg-red-100 text-red-700" },
    RECOMMENDATION: { label: "Recommendation", cls: "bg-violet-100 text-violet-700" },
    PATENT: { label: "Patent", cls: "bg-blue-100 text-blue-700" },
    RESEARCH_TREND: { label: "Trend", cls: "bg-amber-100 text-amber-700" },
    SYSTEM: { label: "System", cls: "bg-slate-100 text-slate-700" },
    API: { label: "API", cls: "bg-slate-100 text-slate-700" },
  };
  const entry = map[type] || { label: type, cls: "bg-slate-100 text-slate-700" };
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${entry.cls}`}>
      {entry.label}
    </span>
  );
}
