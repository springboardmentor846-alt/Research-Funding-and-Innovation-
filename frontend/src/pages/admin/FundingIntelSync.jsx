import React, { useEffect, useMemo, useState } from "react";
import { fundingIntelAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  StatCard,
  Pagination,
  useToasts,
  ToastStack,
  Field,
} from "../../components/admin/ui.jsx";

const PROVIDER_LABELS = {
  nih: "NIH RePORTER",
  grants_gov: "Grants.gov",
  nsf: "NSF Awards",
  cordis: "CORDIS (EU)",
};

function statusTone(status) {
  switch (status) {
    case "healthy": return "success";
    case "degraded": return "warning";
    case "error": return "danger";
    case "disabled": return "slate";
    case "running": return "primary";
    case "paused": return "warning";
    default: return "slate";
  }
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString();
}

function relTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (Number.isNaN(diff)) return "—";
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function FundingIntelSync() {
  const { toasts, pushToast, dismissToast } = useToasts();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [syncForm, setSyncForm] = useState({ provider: "", mode: "incremental", force: false });

  const [logs, setLogs] = useState({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [logsLoading, setLogsLoading] = useState(false);
  const [failed, setFailed] = useState({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [failedLoading, setFailedLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
    loadLogs(1);
    loadFailed(1);
    // Poll the dashboard every 30s while the page is open so the
    // admin sees health/sync status update without manual refresh.
    const id = setInterval(() => loadDashboard(true), 30_000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadDashboard(silent = false) {
    if (!silent) setLoading(true);
    setError("");
    try {
      const res = await fundingIntelAPI.dashboard();
      setDashboard(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load Funding Intelligence dashboard.");
    } finally {
      if (!silent) setLoading(false);
    }
  }

  async function loadLogs(page = 1) {
    setLogsLoading(true);
    try {
      const res = await fundingIntelAPI.logs({ page, page_size: 10 });
      setLogs(res.data);
    } catch (err) {
      // non-blocking
    } finally {
      setLogsLoading(false);
    }
  }

  async function loadFailed(page = 1) {
    setFailedLoading(true);
    try {
      const res = await fundingIntelAPI.failedRecords({ page, page_size: 10 });
      setFailed(res.data);
    } catch (err) {
      // non-blocking
    } finally {
      setFailedLoading(false);
    }
  }

  async function handleSync() {
    setSyncing(true);
    try {
      const payload = {
        mode: syncForm.mode,
        force: syncForm.force,
      };
      if (syncForm.provider) payload.provider = syncForm.provider;
      await fundingIntelAPI.triggerSync(payload);
      pushToast("Sync triggered successfully", "success");
      await loadDashboard(true);
      await loadLogs(1);
    } catch (err) {
      const detail = err.response?.data?.detail;
      pushToast(typeof detail === "string" ? detail : "Sync failed", "error");
    } finally {
      setSyncing(false);
    }
  }

  async function handlePauseToggle() {
    try {
      if (dashboard?.sync_status === "paused") {
        await fundingIntelAPI.resumeSync();
        pushToast("Sync resumed", "success");
      } else {
        await fundingIntelAPI.pauseSync();
        pushToast("Sync paused", "success");
      }
      await loadDashboard(true);
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to change sync state", "error");
    }
  }

  const providers = useMemo(
    () => dashboard?.providers || [],
    [dashboard]
  );

  if (loading && !dashboard) {
    return <PageLoader label="Loading Funding Intelligence dashboard..." />;
  }
  if (error && !dashboard) {
    return <ErrorBanner message={error} onRetry={() => loadDashboard()} />;
  }
  if (!dashboard) return null;

  return (
    <div className="space-y-6">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Funding Intelligence</h1>
          <p className="text-slate-500 text-sm">
            Automated funding ingestion from official providers — NIH, Grants.gov, NSF, CORDIS.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePauseToggle}
            className="btn-secondary text-sm"
            disabled={syncing}
          >
            {dashboard.sync_status === "paused" ? "▶ Resume Sync" : "⏸ Pause Sync"}
          </button>
          <button
            onClick={handleSync}
            className="btn-primary text-sm"
            disabled={syncing || dashboard.sync_status === "paused"}
          >
            {syncing ? "Syncing..." : "↻ Run Sync Now"}
          </button>
        </div>
      </div>

      {/* Top KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <StatCard
          title="Providers Connected"
          value={`${dashboard.apis_connected}/${dashboard.apis_enabled}`}
          subtitle={`${dashboard.apis_healthy} healthy`}
          color="green"
          icon="🔌"
        />
        <StatCard
          title="Funding Total"
          value={dashboard.funding_total}
          subtitle={`${dashboard.funding_active} active`}
          color="primary"
          icon="💰"
        />
        <StatCard
          title="Imported Today"
          value={dashboard.funding_imported_today}
          subtitle="New opportunities"
          color="blue"
          icon="⬇"
        />
        <StatCard
          title="Updated Today"
          value={dashboard.funding_updated_today}
          subtitle="Records refreshed"
          color="purple"
          icon="✎"
        />
        <StatCard
          title="Duplicates Removed"
          value={dashboard.duplicates_removed_today}
          subtitle="Today"
          color="amber"
          icon="🧬"
        />
        <StatCard
          title="Expired"
          value={dashboard.expired_today}
          subtitle="Auto-archived today"
          color="red"
          icon="⌛"
        />
        <StatCard
          title="Error Rate"
          value={`${(dashboard.error_rate_pct ?? 0).toFixed(1)}%`}
          subtitle="Last 24h"
          color="slate"
          icon="📈"
        />
      </div>

      <div className="card grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
        <div>
          <div className="text-xs text-slate-500">Sync Status</div>
          <div className="mt-1">
            <Badge tone={statusTone(dashboard.sync_status)}>{dashboard.sync_status}</Badge>
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Last Sync</div>
          <div className="text-slate-700">{fmtDate(dashboard.last_sync_at)} ({relTime(dashboard.last_sync_at)})</div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Next Scheduled</div>
          <div className="text-slate-700">{fmtDate(dashboard.next_sync_at)}</div>
        </div>
      </div>

      {/* Sync control panel */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">Sync Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
          <Field label="Provider">
            <select
              className="input"
              value={syncForm.provider}
              onChange={(e) => setSyncForm({ ...syncForm, provider: e.target.value })}
            >
              <option value="">All enabled providers</option>
              {providers
                .filter((p) => p.enabled)
                .map((p) => (
                  <option key={p.name} value={p.name}>
                    {PROVIDER_LABELS[p.name] || p.name}
                  </option>
                ))}
            </select>
          </Field>
          <Field label="Mode">
            <select
              className="input"
              value={syncForm.mode}
              onChange={(e) => setSyncForm({ ...syncForm, mode: e.target.value })}
            >
              <option value="incremental">Incremental</option>
              <option value="full">Full</option>
            </select>
          </Field>
          <label className="flex items-center gap-2 text-sm text-slate-700 mt-6">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-slate-300 text-primary-600"
              checked={syncForm.force}
              onChange={(e) => setSyncForm({ ...syncForm, force: e.target.checked })}
            />
            Force (run even when paused)
          </label>
          <button
            type="button"
            onClick={handleSync}
            className="btn-primary"
            disabled={syncing || (!syncForm.force && dashboard.sync_status === "paused")}
          >
            {syncing ? "Running..." : "Start Sync"}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Incremental syncs use the latest cursor; full syncs re-fetch every page from the upstream.
          Successful syncs upsert existing records — no duplicate rows are created.
        </p>
      </div>

      {/* Provider health */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">API Health</h3>
        {providers.length === 0 ? (
          <p className="text-sm text-slate-500">No providers registered.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
                <tr>
                  <th className="text-left px-3 py-2">Provider</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Last Checked</th>
                  <th className="text-left px-3 py-2">Last Success</th>
                  <th className="text-left px-3 py-2">Avg Resp</th>
                  <th className="text-left px-3 py-2">Consec. Failures</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {providers.map((p) => (
                  <tr key={p.name} className="hover:bg-slate-50">
                    <td className="px-3 py-2">
                      <div className="font-medium text-slate-800">{PROVIDER_LABELS[p.name] || p.name}</div>
                      <div className="text-xs text-slate-500">{p.name}</div>
                    </td>
                    <td className="px-3 py-2">
                      <Badge tone={statusTone(p.status)}>{p.status}</Badge>
                      {!p.enabled && <Badge tone="slate">disabled</Badge>}
                    </td>
                    <td className="px-3 py-2 text-slate-600">{relTime(p.last_checked)}</td>
                    <td className="px-3 py-2 text-slate-600">{relTime(p.last_success)}</td>
                    <td className="px-3 py-2 text-slate-600">
                      {p.last_response_ms ? `${p.last_response_ms.toFixed(0)} ms` : "—"}
                    </td>
                    <td className="px-3 py-2">
                      {p.consecutive_failures > 0 ? (
                        <Badge tone="danger">{p.consecutive_failures}</Badge>
                      ) : (
                        <span className="text-slate-400">0</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent runs */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">Recent Sync Runs</h3>
          <button className="btn-secondary text-xs" onClick={() => loadLogs(1)} disabled={logsLoading}>
            Refresh
          </button>
        </div>
        {logsLoading ? (
          <PageLoader label="Loading sync logs..." />
        ) : logs.items.length === 0 ? (
          <EmptyState title="No sync runs yet" description="Trigger a sync to populate this view." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
                <tr>
                  <th className="text-left px-3 py-2">Run</th>
                  <th className="text-left px-3 py-2">Provider</th>
                  <th className="text-left px-3 py-2">Mode</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Fetched</th>
                  <th className="text-left px-3 py-2">Inserted</th>
                  <th className="text-left px-3 py-2">Updated</th>
                  <th className="text-left px-3 py-2">Expired</th>
                  <th className="text-left px-3 py-2">Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.items.map((r) => (
                  <tr key={r.run_id} className="hover:bg-slate-50">
                    <td className="px-3 py-2 text-slate-600">#{r.run_id}</td>
                    <td className="px-3 py-2 text-slate-800">{PROVIDER_LABELS[r.provider] || r.provider}</td>
                    <td className="px-3 py-2"><Badge tone="primary">{r.mode}</Badge></td>
                    <td className="px-3 py-2"><Badge tone={statusTone(r.status)}>{r.status}</Badge></td>
                    <td className="px-3 py-2 text-slate-700">{r.records_fetched}</td>
                    <td className="px-3 py-2 text-green-700">{r.records_inserted}</td>
                    <td className="px-3 py-2 text-blue-700">{r.records_updated}</td>
                    <td className="px-3 py-2 text-amber-700">{r.expired_marked}</td>
                    <td className="px-3 py-2 text-slate-500 text-xs">
                      {r.duration_ms ? `${(r.duration_ms / 1000).toFixed(1)}s` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {logs.total_pages > 1 && (
          <Pagination page={logs.page} totalPages={logs.total_pages} onChange={loadLogs} />
        )}
      </div>

      {/* Failed records */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">Failed Records</h3>
          <button className="btn-secondary text-xs" onClick={() => loadFailed(1)} disabled={failedLoading}>
            Refresh
          </button>
        </div>
        {failedLoading ? (
          <PageLoader label="Loading failures..." />
        ) : failed.items.length === 0 ? (
          <EmptyState title="No failures" description="Recent syncs have processed every record cleanly." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
                <tr>
                  <th className="text-left px-3 py-2">Provider</th>
                  <th className="text-left px-3 py-2">Source ID</th>
                  <th className="text-left px-3 py-2">Type</th>
                  <th className="text-left px-3 py-2">Message</th>
                  <th className="text-left px-3 py-2">Occurred</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {failed.items.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50">
                    <td className="px-3 py-2">{PROVIDER_LABELS[f.provider] || f.provider}</td>
                    <td className="px-3 py-2 text-slate-500 text-xs">{f.source_id || "—"}</td>
                    <td className="px-3 py-2"><Badge tone="warning">{f.error_type}</Badge></td>
                    <td className="px-3 py-2 text-slate-700 max-w-[480px] truncate" title={f.error_message}>{f.error_message}</td>
                    <td className="px-3 py-2 text-xs text-slate-500">{relTime(f.occurred_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {failed.total_pages > 1 && (
          <Pagination page={failed.page} totalPages={failed.total_pages} onChange={loadFailed} />
        )}
      </div>
    </div>
  );
}
