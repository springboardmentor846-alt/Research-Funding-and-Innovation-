import React, { useEffect, useMemo, useState } from "react";
import { patentsIntelAPI } from "../../services/api.js";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Line, Doughnut } from "react-chartjs-2";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  StatCard,
  useToasts,
  ToastStack,
} from "../../components/admin/ui.jsx";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const CHART_PALETTE = [
  "#3b82f6",
  "#8b5cf6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#ec4899",
  "#6366f1",
];

function fmtNum(v) {
  if (v === null || v === undefined) return "—";
  return Number(v).toLocaleString();
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

function statusTone(status) {
  switch (status) {
    case "healthy":
      return "success";
    case "degraded":
      return "warning";
    case "error":
    case "failed":
      return "danger";
    case "disabled":
      return "slate";
    case "running":
      return "primary";
    case "paused":
    case "skipped":
      return "warning";
    case "success":
      return "success";
    default:
      return "slate";
  }
}

function RecommendationRow({ rec }) {
  return (
    <tr className="hover:bg-slate-50">
      <td className="px-4 py-3 text-sm font-medium text-slate-800 max-w-[260px] truncate">
        {rec.title}
      </td>
      <td className="px-4 py-3 text-xs text-slate-500 font-mono">
        {rec.patent_number}
      </td>
      <td className="px-4 py-3 text-sm text-slate-600 max-w-[180px] truncate">
        {rec.assignee || "—"}
      </td>
      <td className="px-4 py-3 text-sm text-slate-600 max-w-[160px] truncate">
        {rec.technology_area || "—"}
      </td>
      <td className="px-4 py-3">
        <Badge tone="primary">{rec.commercialization_label}</Badge>
      </td>
      <td className="px-4 py-3 text-right text-sm font-semibold text-slate-800">
        {rec.innovation_score?.toFixed(2)}
      </td>
      <td className="px-4 py-3 text-right text-sm text-slate-600">
        {rec.citations ?? 0}
      </td>
    </tr>
  );
}

export default function PatentIntel() {
  const { toasts, pushToast, dismissToast } = useToasts();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [recomputing, setRecomputing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load(forceRefresh = false) {
    setLoading(true);
    setError("");
    try {
      const res = await patentsIntelAPI.dashboard(forceRefresh);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load patent intelligence");
    } finally {
      setLoading(false);
    }
  }

  async function handleRefreshDashboard() {
    setRefreshing(true);
    try {
      await patentsIntelAPI.refreshDashboard();
      await load(true);
      pushToast("Dashboard refreshed", "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Refresh failed", "error");
    } finally {
      setRefreshing(false);
    }
  }

  async function handleRecomputeScores() {
    setRecomputing(true);
    try {
      const res = await patentsIntelAPI.recomputeScores();
      pushToast(
        `Innovation scores recomputed (${res.data.computed} patents, avg ${res.data.avg_final_score?.toFixed(2)})`,
        "success"
      );
      await load(true);
    } catch (err) {
      pushToast(err.response?.data?.detail || "Recompute failed", "error");
    } finally {
      setRecomputing(false);
    }
  }

  async function handleTriggerSync() {
    setSyncing(true);
    try {
      const res = await patentsIntelAPI.triggerSync({ mode: "incremental", force: false });
      const t = res.data.totals || {};
      pushToast(
        `Sync finished: ${t.fetched || 0} fetched, ${t.inserted || 0} inserted, ${t.updated || 0} updated`,
        "success"
      );
      await load(true);
    } catch (err) {
      pushToast(err.response?.data?.detail || "Sync failed", "error");
    } finally {
      setSyncing(false);
    }
  }

  const filteredRecommendations = useMemo(() => {
    if (!data?.recommendations) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data.recommendations;
    return data.recommendations.filter(
      (r) =>
        r.title?.toLowerCase().includes(q) ||
        r.assignee?.toLowerCase().includes(q) ||
        r.technology_area?.toLowerCase().includes(q) ||
        r.commercialization_label?.toLowerCase().includes(q)
    );
  }, [data, search]);

  // ----- Chart datasets -----------------------------------------------------
  const bySourceChart = useMemo(() => {
    const arr = data?.analytics?.by_source || [];
    return {
      labels: arr.map((b) => b.source),
      datasets: [
        {
          label: "Patents",
          data: arr.map((b) => b.count),
          backgroundColor: arr.map((_, i) => CHART_PALETTE[i % CHART_PALETTE.length]),
        },
      ],
    };
  }, [data]);

  const byYearChart = useMemo(() => {
    const arr = data?.analytics?.by_year || [];
    return {
      labels: arr.map((b) => b.year),
      datasets: [
        {
          label: "Patents",
          data: arr.map((b) => b.count),
          backgroundColor: "#3b82f6",
        },
        {
          label: "Citations",
          data: arr.map((b) => b.citations),
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.1)",
          type: "line",
          tension: 0.4,
          yAxisID: "y1",
        },
      ],
    };
  }, [data]);

  const byTechnologyChart = useMemo(() => {
    const arr = (data?.analytics?.by_technology || []).slice(0, 10);
    return {
      labels: arr.map((b) => b.technology),
      datasets: [
        {
          label: "Patents",
          data: arr.map((b) => b.count),
          backgroundColor: "#8b5cf6",
        },
      ],
    };
  }, [data]);

  if (loading) return <PageLoader label="Loading patent intelligence..." />;
  if (error) return <ErrorBanner message={error} onRetry={() => load(false)} />;
  if (!data) return null;

  const analytics = data.analytics || {};
  const tech = data.technology_intelligence || {};
  const citations = analytics.citation_stats || {};
  const summary = data.commercialization_summary || {};
  const emerging = tech.emerging_technologies || [];
  const fastGrowing = tech.fast_growing_technologies || [];
  const clusters = tech.clusters || [];
  const highlyCited = tech.highly_cited_patents || [];
  const topAssignees = analytics.top_assignees || [];

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🛰️ Patent Intelligence
          </h1>
          <p className="text-slate-500 text-sm">
            Operator console — refresh dashboard, recompute scores, trigger sync
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleRecomputeScores}
            disabled={recomputing}
            className="btn-secondary text-sm"
          >
            {recomputing ? "Recomputing…" : "⚙️ Recompute Scores"}
          </button>
          <button
            onClick={handleTriggerSync}
            disabled={syncing}
            className="btn-secondary text-sm"
          >
            {syncing ? "Syncing…" : "🔄 Run Provider Sync"}
          </button>
          <button
            onClick={handleRefreshDashboard}
            disabled={refreshing}
            className="btn-primary text-sm"
          >
            {refreshing ? "Refreshing…" : "📊 Refresh Dashboard"}
          </button>
        </div>
      </div>

      <div className="card bg-blue-50 border-blue-200 text-blue-800 text-sm">
        ℹ️ Every figure on this page comes from the live <code>patents</code> table populated by the Patent Intelligence Service. The dashboard cache is 5 minutes; use the buttons above to force a refresh.
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          title="Total Patents"
          value={fmtNum(data.total_patents)}
          subtitle="Live corpus"
          color="primary"
          icon="📄"
        />
        <StatCard
          title="Total Citations"
          value={fmtNum(data.total_citations)}
          subtitle={`Avg ${citations.average?.toFixed(2) ?? "—"} per patent`}
          color="purple"
          icon="📚"
        />
        <StatCard
          title="Avg Innovation Score"
          value={data.innovation_score_avg?.toFixed(2) ?? "—"}
          subtitle="0–1 weighted scale"
          color="green"
          icon="💡"
        />
        <StatCard
          title="Recommendations"
          value={data.recommendations?.length || 0}
          subtitle={`${Object.keys(summary).length} distinct labels`}
          color="amber"
          icon="🚀"
        />
      </div>

      {/* Last refresh + cache info */}
      <div className="card text-xs text-slate-500 flex flex-wrap justify-between">
        <span>
          Last refresh: <strong>{fmtDate(data.generated_at)}</strong> ({relTime(data.generated_at)})
        </span>
        <span>Cache TTL: 300s</span>
      </div>

      {/* Charts grid */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">Patents by Source</h3>
          {bySourceChart.labels.length > 0 ? (
            <Doughnut data={bySourceChart} options={{ responsive: true }} />
          ) : (
            <ChartEmpty text="No source data yet" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">
            Growth Trend (Patents & Citations)
          </h3>
          {byYearChart.labels.length > 0 ? (
            <Bar
              data={byYearChart}
              options={{
                responsive: true,
                scales: {
                  y: { beginAtZero: true, title: { display: true, text: "Patents" } },
                  y1: {
                    beginAtZero: true,
                    position: "right",
                    title: { display: true, text: "Citations" },
                    grid: { drawOnChartArea: false },
                  },
                },
              }}
            />
          ) : (
            <ChartEmpty text="No year data yet" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">Top Technologies</h3>
          {byTechnologyChart.labels.length > 0 ? (
            <Bar
              data={byTechnologyChart}
              options={{
                responsive: true,
                indexAxis: "y",
                scales: { x: { beginAtZero: true } },
              }}
            />
          ) : (
            <ChartEmpty text="No technology data yet" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">Citation Stats</h3>
          <KV label="Total" value={fmtNum(citations.total)} />
          <KV label="Average" value={citations.average?.toFixed(2) ?? "—"} />
          <KV label="Max" value={fmtNum(citations.max)} />
          <KV label="Highly Cited (≥10)" value={fmtNum(citations.highly_cited_count)} />
        </div>
      </div>

      {/* Top assignees + emerging */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">
            🏢 Most Active Organizations
          </h3>
          {topAssignees.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {topAssignees.map((a, i) => (
                <div key={i} className="flex items-center justify-between py-2">
                  <span className="text-sm text-slate-700 truncate flex-1">
                    {a.assignee}
                  </span>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge tone="primary">{a.count}</Badge>
                    <Badge tone="success">📚 {a.total_citations}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <ChartEmpty text="No assignee data yet" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">
            🚀 Emerging + ⚡ Fast-Growing
          </h3>
          {emerging.length === 0 && fastGrowing.length === 0 ? (
            <ChartEmpty text="No growth signals yet" />
          ) : (
            <div className="divide-y divide-slate-100">
              {emerging.map((t, i) => (
                <div key={`e-${i}`} className="flex items-center justify-between py-2">
                  <div>
                    <div className="font-medium text-slate-800 text-sm">
                      {t.technology_area}
                    </div>
                    <div className="text-xs text-slate-500">
                      {t.patent_count} patents · {t.publication_year}
                    </div>
                  </div>
                  <Badge tone="success">
                    emerging · +{((t.growth_rate || 0) * 100).toFixed(0)}%
                  </Badge>
                </div>
              ))}
              {fastGrowing.map((t, i) => (
                <div key={`f-${i}`} className="flex items-center justify-between py-2">
                  <div>
                    <div className="font-medium text-slate-800 text-sm">
                      {t.technology_area}
                    </div>
                    <div className="text-xs text-slate-500">
                      {t.patent_count} patents · {t.publication_year}
                    </div>
                  </div>
                  <Badge tone="warning">
                    fast-growing · +{((t.growth_rate || 0) * 100).toFixed(0)}%
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Clusters + highly cited */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">
            🎯 Technology Clusters (K-Means)
          </h3>
          {clusters.length > 0 ? (
            <div className="grid sm:grid-cols-2 gap-3">
              {clusters.map((c) => (
                <div key={c.cluster_id} className="p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-slate-800">
                      {c.label || `Cluster ${c.cluster_id}`}
                    </span>
                    <Badge tone="purple">{c.size}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {(c.keywords || []).slice(0, 5).map((k) => (
                      <span
                        key={k}
                        className="text-xs px-2 py-0.5 bg-primary-100 text-primary-800 rounded-full"
                      >
                        {k}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <ChartEmpty text="No clusters yet" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">🏆 Highly Cited</h3>
          {highlyCited.length > 0 ? (
            <div>
              {highlyCited.slice(0, 8).map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-slate-800 text-sm truncate">
                      {p.title}
                    </div>
                    <div className="text-xs text-slate-500">
                      {p.assignee || "Unknown"} · {p.publication_year || "—"}
                    </div>
                  </div>
                  <Badge tone="success">📚 {p.citations}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <ChartEmpty text="No citations yet" />
          )}
        </div>
      </div>

      {/* Commercialization summary */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">
          💼 Commercialization Summary
        </h3>
        {Object.keys(summary).length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {Object.entries(summary).map(([label, count]) => (
              <span key={label} className="badge-primary text-sm">
                {label}: <strong className="ml-1">{count}</strong>
              </span>
            ))}
          </div>
        ) : (
          <ChartEmpty text="No commercialization labels yet" />
        )}
      </div>

      {/* Recommendations table */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <h3 className="font-semibold text-slate-800">
            🎯 Top Commercialization Recommendations
          </h3>
          <input
            className="input text-sm max-w-[280px]"
            placeholder="Filter by title, assignee, label..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {filteredRecommendations.length === 0 ? (
          <EmptyState
            title="No recommendations yet"
            description="Use the buttons above to recompute scores and refresh the dashboard."
          />
        ) : (
          <div className="overflow-x-auto -mx-4">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
                <tr>
                  <th className="text-left px-4 py-3">Title</th>
                  <th className="text-left px-4 py-3">Patent #</th>
                  <th className="text-left px-4 py-3">Assignee</th>
                  <th className="text-left px-4 py-3">Technology</th>
                  <th className="text-left px-4 py-3">Label</th>
                  <th className="text-right px-4 py-3">Score</th>
                  <th className="text-right px-4 py-3">Citations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredRecommendations.map((r) => (
                  <RecommendationRow key={r.patent_id} rec={r} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function ChartEmpty({ text }) {
  return (
    <div className="h-40 flex items-center justify-center text-slate-400 text-sm">
      {text}
    </div>
  );
}

function KV({ label, value }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="font-semibold text-slate-800">{value}</span>
    </div>
  );
}
