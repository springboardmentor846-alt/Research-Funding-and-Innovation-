import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useNotifications } from "../context/NotificationsContext.jsx";

/**
 * Notification bell + dropdown mounted in the MainLayout header.
 *
 * - Shows the unread count from the notifications context.
 * - Click toggles a dropdown panel with the most recent items.
 * - Selecting a row marks it as read and navigates to its action_url.
 * - "View All" goes to /notifications, "Mark all as read" empties the
 *   counter.
 *
 * Styling deliberately reuses the project's tailwind tokens (card,
 * btn-ghost, badge, etc.) so it feels native to the dashboard.
 */
export default function NotificationBell() {
  const { unreadCount, recent, markAsRead, markAllAsRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);
  const navigate = useNavigate();

  // Close on outside click.
  useEffect(() => {
    function onDocClick(e) {
      if (!wrapperRef.current) return;
      if (!wrapperRef.current.contains(e.target)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  // Close on route change.
  useEffect(() => {
    return () => setOpen(false);
  }, [navigate]);

  async function handleSelect(n) {
    if (!n.is_read) await markAsRead(n.id);
    setOpen(false);
    if (n.action_url) navigate(n.action_url);
  }

  return (
    <div className="relative" ref={wrapperRef}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="relative inline-flex items-center justify-center w-10 h-10 rounded-full text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
        aria-label={`Notifications, ${unreadCount} unread`}
        title="Notifications"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.8}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75V8A6 6 0 006 8v1.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
          />
        </svg>
        {unreadCount > 0 && (
          <span
            className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-semibold flex items-center justify-center"
            data-testid="notif-badge"
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          className="absolute right-0 mt-2 w-96 max-w-[90vw] bg-white rounded-xl shadow-lg border border-slate-200 z-40 overflow-hidden"
          role="menu"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
            <div className="font-semibold text-slate-800">Notifications</div>
            <div className="text-xs text-slate-500">
              {unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}
            </div>
          </div>

          <div className="max-h-[60vh] overflow-y-auto">
            {recent.length === 0 ? (
              <div className="p-6 text-center text-sm text-slate-500">
                No notifications yet. We'll surface new funding
                opportunities, deadlines, and updates here.
              </div>
            ) : (
              <ul className="divide-y divide-slate-100">
                {recent.map((n) => (
                  <li key={n.id}>
                    <button
                      type="button"
                      onClick={() => handleSelect(n)}
                      className={`w-full text-left px-4 py-3 flex items-start gap-3 hover:bg-slate-50 ${
                        n.is_read ? "" : "bg-primary-50/40"
                      }`}
                    >
                      <PriorityDot priority={n.priority} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <div
                            className={`text-sm font-medium truncate ${
                              n.is_read
                                ? "text-slate-600"
                                : "text-slate-800"
                            }`}
                          >
                            {n.title}
                          </div>
                          <TypeBadge type={n.notification_type} />
                        </div>
                        <div className="text-xs text-slate-500 line-clamp-2 mt-0.5">
                          {n.message}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">
                          {formatRelative(n.created_at)}
                        </div>
                      </div>
                      {!n.is_read && (
                        <span
                          className="mt-1.5 inline-block w-2 h-2 rounded-full bg-primary-500"
                          aria-label="unread"
                        />
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex items-center justify-between px-4 py-2 border-t border-slate-100 bg-slate-50">
            <Link
              to="/notifications"
              onClick={() => setOpen(false)}
              className="text-sm text-primary-600 hover:underline"
            >
              View All Notifications
            </Link>
            <button
              type="button"
              onClick={() => {
                markAllAsRead();
                setOpen(false);
              }}
              className="text-sm text-slate-600 hover:text-slate-800 disabled:opacity-50"
              disabled={unreadCount === 0}
            >
              Mark all as read
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function PriorityDot({ priority }) {
  const cls =
    priority === "CRITICAL"
      ? "bg-red-500"
      : priority === "HIGH"
      ? "bg-amber-500"
      : priority === "LOW"
      ? "bg-slate-300"
      : "bg-primary-500";
  return (
    <span
      className={`mt-1.5 inline-block w-2.5 h-2.5 rounded-full flex-shrink-0 ${cls}`}
      title={`Priority: ${priority}`}
    />
  );
}

function TypeBadge({ type }) {
  const map = {
    FUNDING_NEW: { label: "Funding", cls: "bg-emerald-100 text-emerald-700" },
    FUNDING_MATCH: { label: "Match", cls: "bg-emerald-100 text-emerald-700" },
    FUNDING_DEADLINE: { label: "Deadline", cls: "bg-red-100 text-red-700" },
    RECOMMENDATION: { label: "Rec", cls: "bg-violet-100 text-violet-700" },
    PATENT: { label: "Patent", cls: "bg-blue-100 text-blue-700" },
    RESEARCH_TREND: { label: "Trend", cls: "bg-amber-100 text-amber-700" },
    SYSTEM: { label: "System", cls: "bg-slate-100 text-slate-700" },
    API: { label: "API", cls: "bg-slate-100 text-slate-700" },
  };
  const entry = map[type] || { label: type, cls: "bg-slate-100 text-slate-700" };
  return (
    <span
      className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${entry.cls}`}
    >
      {entry.label}
    </span>
  );
}

function formatRelative(iso) {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  const now = Date.now();
  const diffSec = Math.max(0, Math.floor((now - then) / 1000));
  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} min ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} hr ago`;
  const days = Math.floor(diffSec / 86400);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;
  return new Date(iso).toLocaleDateString();
}
