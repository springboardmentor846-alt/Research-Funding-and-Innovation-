import React, { useEffect, useMemo, useState } from "react";
import { patentsIntelAPI } from "../services/api.js";
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

// Sequential palette aligned with the rest of the dashboard (primary blue /
// purple / green / amber / red / cyan).  Used as a fallback when the corpus
// is sparse so charts never render empty.
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

function fmtPct(v) {
  if (v === null || v === undefined) return "—";
  return `${(v * 100).toFixed(0)}%`;
}

function fmtNum(v) {
  if (v === null || v === undefined) return "—";
  return Number(v).toLocaleString();
}

function RecommendationCard({ rec }) {
  // Color tone for each commercialization label — keeps the
  // recommendation visually scannable.
  const tones = {
    "High Commercial Potential": "success",
    "Strong Licensing Opportunity": "primary",
    "Emerging Technology": "purple",
    "Highly Competitive Technology": "warning",
    "Consider Patent Filing": "blue",
  };
  const tone = tones[rec.commercialization_label] || "slate";
  return (
    <div className="card hover:shadow-md transition">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${tone}-100 text-${tone}-800`}
        >
          {rec.commercialization_label}
        </span>
        <span className="badge-primary">Score {rec.innovation_score?.toFixed(2)}</span>
        <span className="badge-success">📚 {rec.citations ?? 0}</span>
        {rec.publication_year && (
          <span className="badge-slate">{rec.publication_year}</span>
        )}
      </div>
      <h3 className="font-semibold text-slate-800 line-clamp-2">{rec.title}</h3>
      <div className="text-xs text-slate-500 mt-1">
        {rec.assignee || "Unknown assignee"} · {rec.technology_area || "Unclassified"}
      </div>
      {rec.commercialization_reason && (
        <p className="text-sm text-slate-600 mt-2">{rec.commercialization_reason}</p>
      )}
    </div>
  );
}

function ClusterCard({ cluster }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-slate-800 text-sm">
          {cluster.label || `Cluster ${cluster.cluster_id}`}
        </h3>
        <span className="badge-purple">{cluster.size} patents</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {(cluster.keywords || []).slice(0, 6).map((k) => (
          <span key={k} className="badge-primary text-xs">
            {k}
          </span>
        ))}
        {(!cluster.keywords || cluster.keywords.length === 0) && (
          <span className="text-xs text-slate-400">No keywords</span>
        )}
      </div>
    </div>
  );
}

function HighCitedRow({ patent }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="font-medium text-slate-800 truncate">{patent.title}</div>
        <div className="text-xs text-slate-500">
          {patent.assignee || "Unknown"} · {patent.technology_area || "Unclassified"} ·{" "}
          {patent.publication_year || "—"}
        </div>
      </div>
      <span className="badge-success ml-3 flex-shrink-0">📚 {patent.citations}</span>
    </div>
  );
}

export default function PatentAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncBanner, setSyncBanner] = useState("");

  useEffect(() => {
    load(false);
  }, []);

  async function load(forceRefresh) {
    setLoading(true);
    setError("");
    try {
      const res = await patentsIntelAPI.dashboard(forceRefresh);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load patent analytics");
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    setError("");
    try {
      await patentsIntelAPI.refreshDashboard();
      await load(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  }

  async function handleManualSync() {
    setSyncing(true);
    setError("");
    setSyncBanner("");
    try {
      const res = await patentsIntelAPI.triggerSync({ mode: "incremental", force: false });
      const totals = res.data?.totals || {};
      const status = res.data?.status || "unknown";
      setSyncBanner(
        `Sync ${status}: fetched ${totals.fetched || 0}, ` +
        `inserted ${totals.inserted || 0}, updated ${totals.updated || 0}, ` +
        `skipped ${totals.skipped || 0}`
      );
      // Refresh the dashboard so newly ingested patents show up.
      await patentsIntelAPI.refreshDashboard();
      await load(true);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Manual sync failed. Check The Lens API token, network, and provider health."
      );
    } finally {
      setSyncing(false);
    }
  }

  // ----- Chart datasets (memoised so re-renders don't reallocate) ---------
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

  const byCountryChart = useMemo(() => {
    const arr = (data?.analytics?.by_country || []).slice(0, 8);
    return {
      labels: arr.map((b) => b.country),
      datasets: [
        {
          data: arr.map((b) => b.count),
          backgroundColor: arr.map((_, i) => CHART_PALETTE[i % CHART_PALETTE.length]),
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 text-red-700 flex items-center justify-between">
        <span>{error}</span>
        <button onClick={() => load(false)} className="btn-secondary text-xs">
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  const analytics = data.analytics || {};
  const tech = data.technology_intelligence || {};
  const citations = analytics.citation_stats || {};
  const topAssignees = analytics.top_assignees || [];
  const topInventors = analytics.top_inventors || [];
  const growth = analytics.growth_trend || [];
  const emerging = tech.emerging_technologies || [];
  const fastGrowing = tech.fast_growing_technologies || [];
  const clusters = tech.clusters || [];
  const highlyCited = tech.highly_cited_patents || [];
  const recommendations = data.recommendations || [];
  const summary = data.commercialization_summary || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            📊 Patent Analytics Dashboard
          </h1>
          <p className="text-slate-500 text-sm">
            Live insights from the canonical patent corpus
            {data.generated_at && (
              <span className="ml-2 text-xs">
                (last refresh {new Date(data.generated_at).toLocaleString()})
              </span>
            )}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-secondary text-sm"
        >
          {refreshing ? "Refreshing…" : "🔄 Refresh All Signals"}
        </button>
      </div>

      {/* KPI Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-slate-500">Total Patents</div>
          <div className="text-3xl font-bold text-primary-600 mt-1">
            {fmtNum(data.total_patents)}
          </div>
          <div className="text-xs text-slate-400 mt-1">Live corpus</div>
        </div>
        <div className="card">
          <div className="text-sm text-slate-500">Total Citations</div>
          <div className="text-3xl font-bold text-purple-600 mt-1">
            {fmtNum(data.total_citations)}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Avg {citations.average?.toFixed(2) ?? "—"} per patent
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-slate-500">Average Innovation Score</div>
          <div className="text-3xl font-bold text-green-600 mt-1">
            {data.innovation_score_avg?.toFixed(2) ?? "—"}
          </div>
          <div className="text-xs text-slate-400 mt-1">0–1 weighted scale</div>
        </div>
        <div className="card">
          <div className="text-sm text-slate-500">Recommendations</div>
          <div className="text-3xl font-bold text-amber-600 mt-1">
            {recommendations.length}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {Object.keys(summary).length} distinct labels
          </div>
        </div>
      </div>

      {/* Patent Landscape Analysis */}
      <section>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">
          🌍 Patent Landscape Analysis
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-slate-800">
              {analytics.by_source?.length || 0}
            </div>
            <div className="text-xs text-slate-500">Sources</div>
          </div>
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-slate-800">
              {analytics.by_technology?.length || 0}
            </div>
            <div className="text-xs text-slate-500">Technology Areas</div>
          </div>
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-slate-800">
              {citations.highly_cited_count ?? 0}
            </div>
            <div className="text-xs text-slate-500">Highly Cited (≥10)</div>
          </div>
        </div>

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
              Growth Trend (Patents & Citations by Year)
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
            <h3 className="font-semibold text-slate-800 mb-3">Technology Distribution</h3>
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
            <h3 className="font-semibold text-slate-800 mb-3">Geographical Spread</h3>
            {byCountryChart.labels.length > 0 ? (
              <Doughnut data={byCountryChart} options={{ responsive: true }} />
            ) : (
              <ChartEmpty text="No country data yet" />
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4 mt-4">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              🏢 Top Assignees (Most Active Organizations)
            </h3>
            {topAssignees.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {topAssignees.map((a, i) => (
                  <div key={i} className="flex items-center justify-between py-2">
                    <span className="text-sm text-slate-700 truncate flex-1">
                      {a.assignee}
                    </span>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className="badge-primary">{a.count}</span>
                      <span className="badge-success text-xs">
                        📚 {a.total_citations}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <ChartEmpty text="No assignee data yet" />
            )}
          </div>

          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">👤 Top Inventors</h3>
            {topInventors.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {topInventors.map((inv, i) => (
                  <div key={i} className="flex items-center justify-between py-2">
                    <span className="text-sm text-slate-700 truncate flex-1">
                      {inv.inventor}
                    </span>
                    <span className="badge-purple">{inv.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <ChartEmpty text="No inventor data yet" />
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-4 mt-4">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-2">Citation Statistics</h3>
            <KV label="Total" value={fmtNum(citations.total)} />
            <KV label="Average" value={citations.average?.toFixed(2) ?? "—"} />
            <KV label="Maximum" value={fmtNum(citations.max)} />
            <KV label="Highly Cited (≥10)" value={fmtNum(citations.highly_cited_count)} />
          </div>

          <div className="lg:col-span-2 card">
            <h3 className="font-semibold text-slate-800 mb-3">Year-over-Year Growth</h3>
            {growth.length > 0 ? (
              <Line
                data={{
                  labels: growth.map((g) => g.year),
                  datasets: [
                    {
                      label: "Patent count",
                      data: growth.map((g) => g.count),
                      borderColor: "#3b82f6",
                      backgroundColor: "rgba(59, 130, 246, 0.1)",
                      tension: 0.4,
                      fill: true,
                      yAxisID: "y",
                    },
                    {
                      label: "Growth rate",
                      data: growth.map((g) =>
                        g.growth_rate === null ? null : +(g.growth_rate * 100).toFixed(2)
                      ),
                      borderColor: "#10b981",
                      backgroundColor: "rgba(16, 185, 129, 0.1)",
                      tension: 0.4,
                      yAxisID: "y1",
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  scales: {
                    y: { beginAtZero: true, title: { display: true, text: "Patents" } },
                    y1: {
                      position: "right",
                      title: { display: true, text: "Growth %" },
                      grid: { drawOnChartArea: false },
                    },
                  },
                }}
              />
            ) : (
              <ChartEmpty text="No growth trend yet" />
            )}
          </div>
        </div>
      </section>

      {/* Technology Intelligence Engine */}
      <section>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">
          🧠 Technology Intelligence Engine
        </h2>
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              🚀 Emerging Technologies
            </h3>
            {emerging.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {emerging.map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-2">
                    <div>
                      <div className="font-medium text-slate-800 text-sm">
                        {t.technology_area}
                      </div>
                      <div className="text-xs text-slate-500">
                        {t.patent_count} patents · {t.total_citations} citations
                      </div>
                    </div>
                    <span className="badge-success">
                      +{((t.growth_rate || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <ChartEmpty text="No emerging technology signal yet" />
            )}
          </div>

          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              ⚡ Fast-Growing Technologies
            </h3>
            {fastGrowing.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {fastGrowing.map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-2">
                    <div>
                      <div className="font-medium text-slate-800 text-sm">
                        {t.technology_area}
                      </div>
                      <div className="text-xs text-slate-500">
                        {t.patent_count} patents · {t.publication_year}
                      </div>
                    </div>
                    <span className="badge-amber">
                      +{((t.growth_rate || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <ChartEmpty text="No fast-growing technology signal yet" />
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4 mt-4">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              🎯 Technology Clusters (K-Means)
            </h3>
            {clusters.length > 0 ? (
              <div className="grid sm:grid-cols-2 gap-3">
                {clusters.map((c) => (
                  <ClusterCard key={c.cluster_id} cluster={c} />
                ))}
              </div>
            ) : (
              <ChartEmpty text="No clusters yet" />
            )}
          </div>

          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              🏆 Highly Cited Patents
            </h3>
            {highlyCited.length > 0 ? (
              <div>
                {highlyCited.slice(0, 8).map((p) => (
                  <HighCitedRow key={p.id} patent={p} />
                ))}
              </div>
            ) : (
              <ChartEmpty text="No citations yet" />
            )}
          </div>
        </div>
      </section>

      {/* Commercialization Recommendations */}
      <section>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">
          💼 Commercialization Recommendations
        </h2>

        {Object.keys(summary).length > 0 && (
          <div className="card mb-4">
            <h3 className="font-semibold text-slate-800 mb-3">
              Summary by Label
            </h3>
            <div className="flex flex-wrap gap-3">
              {Object.entries(summary).map(([label, count]) => (
                <span key={label} className="badge-primary text-sm">
                  {label}: <strong className="ml-1">{count}</strong>
                </span>
              ))}
            </div>
          </div>
        )}

        {recommendations.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {recommendations.map((rec) => (
              <RecommendationCard key={rec.patent_id} rec={rec} />
            ))}
          </div>
        ) : (
          <ChartEmpty text="No commercialization recommendations yet" />
        )}
      </section>
    </div>
  );
}

function ChartEmpty({ text }) {
  return (
    <div className="h-48 flex items-center justify-center text-slate-400 text-sm">
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
