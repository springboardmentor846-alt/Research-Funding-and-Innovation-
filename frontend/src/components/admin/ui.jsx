import React from "react";
import { useAuth } from "../../context/AuthContext.jsx";

/**
 * Page-level loading spinner, sized to fill the available content area.
 */
export function PageLoader({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  );
}

/**
 * Error banner with optional retry button.
 */
export function ErrorBanner({ message, onRetry }) {
  return (
    <div className="card bg-red-50 border border-red-200 text-red-700 flex items-center justify-between gap-3">
      <span>{message}</span>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-xs">
          Retry
        </button>
      )}
    </div>
  );
}

/**
 * Empty-state card.
 */
export function EmptyState({ title, description, action }) {
  return (
    <div className="card text-center py-12">
      <h3 className="text-base font-semibold text-slate-800">{title}</h3>
      {description && (
        <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

/**
 * Stat tile — used on the admin dashboard.
 */
export function StatCard({ title, value, subtitle, color = "primary", icon, onClick }) {
  const palette = STAT_COLORS[color] || STAT_COLORS.primary;
  const Wrapper = onClick ? "button" : "div";
  return (
    <Wrapper
      onClick={onClick}
      className={`card hover:shadow-md transition text-left w-full ${onClick ? "cursor-pointer" : ""}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-slate-500">{title}</div>
          <div className={`text-3xl font-bold mt-1 ${palette.text}`}>{value ?? "—"}</div>
          {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
        </div>
        {icon && <div className="text-3xl opacity-60">{icon}</div>}
      </div>
    </Wrapper>
  );
}

const STAT_COLORS = {
  primary: { text: "text-primary-600" },
  purple: { text: "text-purple-600" },
  green: { text: "text-green-600" },
  amber: { text: "text-amber-600" },
  red: { text: "text-red-600" },
  blue: { text: "text-blue-600" },
  slate: { text: "text-slate-700" },
};

/**
 * Badge variants used across the admin tables.
 */
export function Badge({ children, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-100 text-slate-800",
    primary: "bg-primary-100 text-primary-800",
    success: "bg-green-100 text-green-800",
    warning: "bg-amber-100 text-amber-800",
    danger: "bg-red-100 text-red-800",
    purple: "bg-purple-100 text-purple-800",
    blue: "bg-blue-100 text-blue-800",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${tones[tone] || tones.slate}`}>
      {children}
    </span>
  );
}

/**
 * Confirm dialog (modal). Designed to be controlled by parent state.
 */
export function ConfirmDialog({
  open,
  title = "Are you sure?",
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  tone = "danger",
  busy = false,
  onConfirm,
  onCancel,
}) {
  if (!open) return null;
  const confirmBtn =
    tone === "danger"
      ? "bg-red-600 hover:bg-red-700 text-white"
      : "bg-primary-600 hover:bg-primary-700 text-white";
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={busy ? undefined : onCancel}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
        {description && (
          <p className="text-sm text-slate-600 mt-2">{description}</p>
        )}
        <div className="flex justify-end gap-2 mt-6">
          <button
            type="button"
            onClick={onCancel}
            disabled={busy}
            className="btn-secondary"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={busy}
            className={`btn ${confirmBtn}`}
          >
            {busy ? "Working..." : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Lightweight toast notifier. Use as a controlled component, with a list of
 * active toasts and an `onDismiss` callback to remove each one.
 */
export function ToastStack({ toasts, onDismiss }) {
  if (!toasts?.length) return null;
  return (
    <div className="fixed top-6 right-6 z-50 space-y-2 w-80">
      {toasts.map((t) => (
        <div
          key={t.id}
          role="alert"
          className={`card flex items-start justify-between gap-3 p-4 shadow-md ${
            t.tone === "success"
              ? "bg-green-50 border-green-200 text-green-800"
              : t.tone === "error"
              ? "bg-red-50 border-red-200 text-red-800"
              : "bg-white text-slate-800"
          }`}
        >
          <span className="text-sm">{t.message}</span>
          <button
            className="text-slate-400 hover:text-slate-700 text-sm"
            onClick={() => onDismiss(t.id)}
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}

/**
 * Hook providing a single `pushToast` and auto-dismiss behaviour.
 *
 * ``pushToast`` accepts two calling shapes so we can keep older callers
 * in the codebase that pass ``{ kind, message }``:
 *
 *   pushToast("Saved", "success")
 *   pushToast({ kind: "success", message: "Saved" })
 *
 * Internally we always normalise to ``(message, tone)``.
 */
import { useCallback, useState } from "react";

function _normalise(input, toneArg) {
  // Object form: { kind, message }
  if (input && typeof input === "object" && !Array.isArray(input)) {
    const kind = input.kind || input.tone || toneArg || "info";
    const tone = kind === "success" ? "success" : kind === "error" ? "error" : "info";
    return { message: String(input.message ?? ""), tone };
  }
  // Positional form: pushToast(message, tone)
  return { message: String(input ?? ""), tone: toneArg || "info" };
}

export function useToasts() {
  const [toasts, setToasts] = useState([]);
  const push = useCallback((input, toneArg = "info", timeout = 3500) => {
    const { message, tone } = _normalise(input, toneArg);
    if (!message) return;
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, tone }]);
    if (timeout) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, timeout);
    }
  }, []);
  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);
  return { toasts, pushToast: push, dismissToast: dismiss };
}

/**
 * Pagination control shared by all admin tables.
 */
export function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-center gap-2">
      <button
        disabled={page === 1}
        onClick={() => onChange(page - 1)}
        className="btn-secondary"
      >
        Prev
      </button>
      <span className="text-sm text-slate-600">
        Page {page} of {totalPages}
      </span>
      <button
        disabled={page === totalPages}
        onClick={() => onChange(page + 1)}
        className="btn-secondary"
      >
        Next
      </button>
    </div>
  );
}

/**
 * Drop a CSV response from the admin API as a download.
 */
export async function downloadFile(response, fallbackName) {
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const cd = response.headers.get("Content-Disposition") || "";
  const match = cd.match(/filename=([^;]+)/);
  a.download = (match ? match[1] : fallbackName).replace(/"/g, "").trim();
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Inline form field with label + error display.
 */
export function Field({ label, error, children, required, hint }) {
  return (
    <div>
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      {children}
      {hint && !error && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
}

/**
 * Re-export `useAuth` for convenience in admin pages.
 */
export { useAuth };
