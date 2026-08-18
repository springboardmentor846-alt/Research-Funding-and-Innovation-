import React, { useEffect, useState } from "react";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  StatCard,
  Badge,
  ConfirmDialog,
  Pagination,
  useToasts,
  ToastStack,
} from "../../components/admin/ui.jsx";

export default function AIRecommendationMonitor() {
  const [stats, setStats] = useState(null);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [userId, setUserId] = useState("");
  const [fundingId, setFundingId] = useState("");
  const [minScore, setMinScore] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [confirm, setConfirm] = useState(null);
  const [regenOpen, setRegenOpen] = useState(false);
  const [regenUserId, setRegenUserId] = useState("");
  const [regenBusy, setRegenBusy] = useState(false);
  const [busy, setBusy] = useState(false);

  const { toasts, pushToast, dismissToast } = useToasts();

  useEffect(() => {
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, userId, fundingId, minScore]);

  async function loadStats() {
    try {
      const res = await adminAPI.recommendationStats();
      setStats(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load AI stats");
    }
  }

  async function load() {
    setLoading(true);
    setError("");
    try {
      const params = {
        page,
        page_size: pageSize,
        ...(userId ? { user_id: Number(userId) } : {}),
        ...(fundingId ? { funding_id: Number(fundingId) } : {}),
        ...(minScore ? { min_score: Number(minScore) } : {}),
      };
      const res = await adminAPI.listRecommendations(params);
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!confirm) return;
    setBusy(true);
    try {
      await adminAPI.deleteRecommendation(confirm.id);
      pushToast("Recommendation record removed", "success");
      setConfirm(null);
      if (items.length === 1 && page > 1) setPage(page - 1);
      else load();
      loadStats();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to remove", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleRegenerate() {
    if (!regenUserId) {
      pushToast("User ID is required", "error");
      return;
    }
    setRegenBusy(true);
    try {
      const res = await adminAPI.regenerateRecommendations(Number(regenUserId));
      pushToast(
        `Regenerated ${res.data.count} recommendations for user #${res.data.user_id}`,
        "success"
      );
      setRegenOpen(false);
      setRegenUserId("");
      load();
      loadStats();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to regenerate", "error");
    } finally {
      setRegenBusy(false);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">AI Recommendation Monitor</h1>
          <p className="text-slate-500 text-sm">
            Monitor and manage platform-wide AI recommendation engine
          </p>
        </div>
        <button onClick={() => setRegenOpen(true)} className="btn-primary text-sm">
          🔄 Regenerate for User
        </button>
      </div>

      <div className="card bg-blue-50 border-blue-200 text-blue-800 text-sm">
        ℹ Admin manages the AI system rather than receiving personalized recommendations. Use the controls below to monitor accuracy and remove incorrect records.
      </div>

      {stats && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Total Generated" value={stats.total_recommendations} subtitle="All time" color="primary" icon="🎯" />
            <StatCard title="Unique Users" value={stats.unique_users} subtitle="With recs" color="purple" icon="👥" />
            <StatCard title="Unique Funding" value={stats.unique_funding} subtitle="Recommended" color="green" icon="💰" />
            <StatCard
              title="Avg Similarity"
              value={Number(stats.avg_similarity_score).toFixed(3)}
              subtitle="Score (0-1)"
              color="amber"
              icon="📊"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="card text-center py-4">
              <div className="text-2xl font-bold text-green-700">{stats.by_quality?.high || 0}</div>
              <div className="text-xs text-slate-500">High (≥0.7)</div>
            </div>
            <div className="card text-center py-4">
              <div className="text-2xl font-bold text-amber-700">{stats.by_quality?.medium || 0}</div>
              <div className="text-xs text-slate-500">Medium (0.4–0.7)</div>
            </div>
            <div className="card text-center py-4">
              <div className="text-2xl font-bold text-red-700">{stats.by_quality?.low || 0}</div>
              <div className="text-xs text-slate-500">{"Low (<0.4)"}</div>
            </div>
          </div>
        </>
      )}

      {error && <ErrorBanner message={error} onRetry={() => { load(); loadStats(); }} />}

      <div className="card flex flex-wrap gap-3">
        <input
          className="input min-w-[140px]"
          placeholder="User ID"
          value={userId}
          onChange={(e) => { setUserId(e.target.value.replace(/[^\d]/g, "")); setPage(1); }}
        />
        <input
          className="input min-w-[140px]"
          placeholder="Funding ID"
          value={fundingId}
          onChange={(e) => { setFundingId(e.target.value.replace(/[^\d]/g, "")); setPage(1); }}
        />
        <input
          className="input min-w-[140px]"
          placeholder="Min score (0-1)"
          value={minScore}
          onChange={(e) => { setMinScore(e.target.value); setPage(1); }}
        />
        <button onClick={() => { setUserId(""); setFundingId(""); setMinScore(""); setPage(1); }} className="btn-secondary text-sm">
          Clear
        </button>
      </div>

      {loading ? (
        <PageLoader label="Loading recommendations..." />
      ) : items.length === 0 ? (
        <EmptyState title="No recommendations found" description="Try adjusting filters." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
              <tr>
                <th className="text-left px-4 py-3">ID</th>
                <th className="text-left px-4 py-3">User</th>
                <th className="text-left px-4 py-3">Funding</th>
                <th className="text-left px-4 py-3">Similarity</th>
                <th className="text-left px-4 py-3">Rule</th>
                <th className="text-left px-4 py-3">Quality</th>
                <th className="text-left px-4 py-3">Created</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((r) => {
                const quality =
                  r.similarity_score >= 0.7
                    ? "success"
                    : r.similarity_score >= 0.4
                    ? "warning"
                    : "danger";
                const qualityLabel =
                  r.similarity_score >= 0.7
                    ? "High"
                    : r.similarity_score >= 0.4
                    ? "Medium"
                    : "Low";
                return (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-500 text-xs">#{r.id}</td>
                    <td className="px-4 py-3 text-slate-700">#{r.user_id}</td>
                    <td className="px-4 py-3 text-slate-700">#{r.funding_id}</td>
                    <td className="px-4 py-3 font-mono text-xs">{Number(r.similarity_score).toFixed(3)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{Number(r.rule_score || 0).toFixed(3)}</td>
                    <td className="px-4 py-3">
                      <Badge tone={quality}>{qualityLabel}</Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {r.created_at ? new Date(r.created_at).toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        className="btn-ghost text-xs text-red-600"
                        disabled={busy}
                        onClick={() => setConfirm(r)}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />

      <ConfirmDialog
        open={!!confirm}
        title="Remove recommendation record"
        description={
          confirm
            ? `Remove recommendation #${confirm.id} (user #${confirm.user_id} → funding #${confirm.funding_id})? This will not regenerate the user's recommendations.`
            : ""
        }
        confirmText="Remove"
        busy={busy}
        onConfirm={handleDelete}
        onCancel={() => !busy && setConfirm(null)}
      />

      {regenOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4" onClick={regenBusy ? undefined : () => setRegenOpen(false)}>
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-md"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-800">Regenerate Recommendations</h2>
              <button onClick={() => setRegenOpen(false)} className="text-slate-500 hover:text-slate-800">✕</button>
            </div>
            <div className="px-6 py-5 space-y-3">
              <p className="text-sm text-slate-600">
                Enter the user ID whose AI recommendations should be regenerated using their current publications.
              </p>
              <label className="label">User ID *</label>
              <input
                className="input"
                value={regenUserId}
                onChange={(e) => setRegenUserId(e.target.value.replace(/[^\d]/g, ""))}
                placeholder="e.g. 12"
              />
            </div>
            <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
              <button
                onClick={() => setRegenOpen(false)}
                className="btn-secondary"
                disabled={regenBusy}
              >
                Cancel
              </button>
              <button
                onClick={handleRegenerate}
                className="btn-primary"
                disabled={regenBusy}
              >
                {regenBusy ? "Regenerating..." : "Regenerate"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
