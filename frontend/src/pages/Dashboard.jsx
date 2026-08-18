import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardAPI, patentsAPI, fundingAPI } from "../services/api.js";
import { useAuth } from "../context/AuthContext.jsx";
import { useSavedPatents } from "../context/SavedPatentsContext.jsx";
import {
  getCachedDashboard,
  setCachedDashboard,
  invalidateDashboardCache,
} from "../utils/dashboardCache.js";
import {
  ToastStack,
  useToasts,
} from "../components/admin/ui.jsx";
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
  RadialLinearScale,
  Filler,
} from "chart.js";
import { Bar, Line, Doughnut, Radar } from "react-chartjs-2";
import Plotly from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";

const Plot = createPlotlyComponent(Plotly);

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
  RadialLinearScale,
  Filler
);

// Static color map — Tailwind JIT can't generate dynamic classes like `text-${color}-600`
const STAT_COLORS = {
  primary: { text: "text-primary-600", bg: "bg-primary-50" },
  purple: { text: "text-purple-600", bg: "bg-purple-50" },
  green: { text: "text-green-600", bg: "bg-green-50" },
  amber: { text: "text-amber-600", bg: "bg-amber-50" },
  red: { text: "text-red-600", bg: "bg-red-50" },
  blue: { text: "text-blue-600", bg: "bg-blue-50" },
};

function StatCard({ title, value, subtitle, color = "primary", icon }) {
  const palette = STAT_COLORS[color] || STAT_COLORS.primary;
  return (
    <div className="card hover:shadow-md transition">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-slate-500">{title}</div>
          <div className={`text-3xl font-bold mt-1 ${palette.text}`}>{value}</div>
          {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  // Read the user id synchronously so the initial render can already
  // pull a cached payload from sessionStorage and skip the spinner on
  // re-entry.  ``useAuth()`` is safe to call here — it returns the
  // current user object synchronously from context.
  const { user } = useAuth();
  const userId = user?.id;
  // Saved-patents KPI: cross-page store hydrates on mount and refreshes
  // after every save/remove elsewhere in the app.
  const { count: savedPatentsCount } = useSavedPatents();

  // Initial state from sessionStorage.  We do this in the ``useState``
  // initializer so the very first render already has data hydrated —
  // no spinner flash when the user navigates back to /dashboard.
  const [data, setData] = useState(() => {
    const cached = getCachedDashboard(userId);
    return cached?.data ?? null;
  });
  // ``loading`` only spins on the first load (cold cache).  On re-entry
  // from another route we hydrate instantly from sessionStorage and
  // ``loading`` starts false — a background refresh kicks off below.
  const [loading, setLoading] = useState(() => {
    return !getCachedDashboard(userId)?.data;
  });
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  // ``hydratedFromCache`` distinguishes "we painted from cache and are
  // refreshing in the background" from "we are doing a fresh fetch".
  const [hydratedFromCache, setHydratedFromCache] = useState(() => {
    return Boolean(getCachedDashboard(userId)?.data);
  });
  const { toasts, pushToast, dismissToast } = useToasts();
  // Guard against out-of-order background refreshes overwriting a
  // newer payload (e.g. user clicks Refresh Recommendations mid-fetch).
  const requestSeq = useRef(0);

  /**
   * Fetch the three dashboard endpoints in parallel and update state.
   * Declared above the useEffect so the effect can call it without
   * relying on JavaScript's declaration hoisting inside a closure.
   */
  async function refreshFromNetwork({
    forceSpinner = false,
    showErrorToast = true,
  } = {}) {
    const seq = ++requestSeq.current;
    if (forceSpinner) setLoading(true);
    try {
      const [overview, patents, fundingStats] = await Promise.all([
        dashboardAPI.overview(),
        patentsAPI.analytics(),
        fundingAPI.stats(),
      ]);
      // Drop the result if a newer request has been issued (avoids a
      // slow background fetch overwriting a fast manual refresh).
      if (seq !== requestSeq.current) return;
      const next = {
        ...overview.data,
        patents: patents.data,
        fundingStats: fundingStats.data,
      };
      setData(next);
      setError("");
      setHydratedFromCache(false);
      setCachedDashboard(userId, next);
    } catch (err) {
      if (seq !== requestSeq.current) return;
      const detail =
        err.response?.data?.detail || "Failed to load dashboard";
      setError(detail);
      if (showErrorToast) {
        pushToast(detail, "error");
      }
    } finally {
      if (seq === requestSeq.current && forceSpinner) {
        setLoading(false);
      }
    }
  }

  useEffect(() => {
    // Stale-while-revalidate:
    //   1. Read the last good payload for this user from sessionStorage.
    //      If present, paint immediately so navigating away and back
    //      does not flash a loading spinner.
    //   2. Kick off a background refresh that updates state + cache.
    //      Failure of the background refresh never blanks the page —
    //      we keep showing the cached numbers and surface the error.
    const cached = getCachedDashboard(userId);
    if (cached?.data) {
      setData(cached.data);
      setLoading(false);
      setHydratedFromCache(true);
    } else {
      setLoading(true);
      setHydratedFromCache(false);
    }

    // Always refresh in the background so the cached payload stays
    // current.  ``forceSpinner`` is true only on the cold-cache path
    // or after an explicit Refresh Recommendations click.
    refreshFromNetwork({
      forceSpinner: !cached?.data,
      showErrorToast: false,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  /**
   * Explicit full reload — used by the "Refresh Recommendations" path
   * so the spinner returns and the user sees they actually triggered
   * a refresh.
   */
  async function reloadWithSpinner() {
    // Drop the cache first so the spinner is mandatory; the next
    // background tick (issued when a fetch lands) repopulates it.
    invalidateDashboardCache(userId);
    setData(null);
    setLoading(true);
    setHydratedFromCache(false);
    await refreshFromNetwork({ forceSpinner: true, showErrorToast: true });
    setLoading(false);
  }

  async function handleRefreshRecommendations() {
    setRefreshing(true);
    try {
      // Pull the user's preferred top-k from the cached recommendations count
      // so the refresh matches whatever was previously rendered; fall back to 10.
      const topK = data?.recommendations_count?.top_k || 10;
      await fundingAPI.refreshRecommendations(topK);
      pushToast("Recommendations refreshed", "success");
      // Refetch the dashboard so any updated cache-derived numbers refresh.
      // This is the manual trigger — show the spinner so the user gets
      // visual feedback that something happened.
      await reloadWithSpinner();
    } catch (err) {
      pushToast(
        err.response?.data?.detail || "Failed to refresh recommendations",
        "error"
      );
    } finally {
      setRefreshing(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return <div className="card bg-red-50 text-red-700">{error}</div>;
  }

  const kpis = data.kpis;
  // Spec-defined flat metrics block — backend computes every value
  // from the database + AI recommender. The UI only renders what the
  // API returns; there are no hardcoded numbers in this file.
  const metrics = data.metrics || {};
  const citationData = {
    labels: (data.citation_trends || []).map((c) => c.year),
    datasets: [
      {
        label: "Citations",
        data: (data.citation_trends || []).map((c) => c.citations),
        borderColor: "rgb(59, 130, 246)",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const domainData = {
    labels: (data.domain_distribution || []).map((d) => d.domain),
    datasets: [
      {
        label: "Publications",
        data: (data.domain_distribution || []).map((d) => d.count),
        backgroundColor: ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#06b6d4"],
      },
    ],
  };

  const growthData = {
    labels: (data.research_growth || []).map((g) => g.year),
    datasets: [
      {
        label: "Publications per Year",
        data: (data.research_growth || []).map((g) => g.publications),
        backgroundColor: "#3b82f6",
      },
    ],
  };

  // Innovation score radar — the values are still the live API metrics
  // (publications, citations, h_index, …) so the chart updates in lock-
  // step with the KPI cards above.
  const radarData = {
    labels: ["Publications", "Citations", "H-Index", "Domains", "Funding Avail.", "Productivity"],
    datasets: [
      {
        label: "Your Profile",
        data: [
          Math.min(100, (metrics.publications || 0) * 5),
          Math.min(100, (metrics.citations || 0) / 5),
          (metrics.h_index || 0) * 5,
          Math.min(100, (data.domain_distribution?.length || 0) * 15),
          Math.min(100, (metrics.available_funding || 0) * 4),
          Math.min(100, (metrics.productivity || 0) * 10),
        ],
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        borderColor: "rgb(59, 130, 246)",
        pointBackgroundColor: "rgb(59, 130, 246)",
      },
    ],
  };

  // Plotly bubble chart: funding opportunities (domain x amount)
  const fundingByDomain = (data.funding_overview?.by_domain || []).map((d, i) => ({
    x: d.domain,
    y: d.count,
    size: Math.max(20, d.count * 15),
    color: ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#06b6d4", "#ef4444"][i % 7],
  }));
  const bubbleTrace = {
    type: "scatter",
    mode: "markers+text",
    x: fundingByDomain.map((d) => d.x),
    y: fundingByDomain.map((d) => d.y),
    text: fundingByDomain.map((d) => `${d.y} opps`),
    textposition: "top center",
    marker: {
      size: fundingByDomain.map((d) => d.size),
      color: fundingByDomain.map((d) => d.color),
      line: { width: 2, color: "white" },
    },
  };
  const bubbleLayout = {
    showlegend: false,
    margin: { l: 40, r: 20, t: 20, b: 60 },
    xaxis: { title: "" },
    yaxis: { title: "Opportunities", rangemode: "tozero" },
    height: 280,
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
  };

  // Plotly 3D-style: research growth + citation trends overlaid
  const growthTrace = {
    x: (data.research_growth || []).map((g) => g.year),
    y: (data.research_growth || []).map((g) => g.publications),
    type: "scatter",
    mode: "lines+markers",
    name: "Publications",
    line: { color: "#3b82f6", width: 3 },
  };
  const citationTrace = {
    x: (data.citation_trends || []).map((c) => c.year),
    y: (data.citation_trends || []).map((c) => c.citations),
    type: "scatter",
    mode: "lines+markers",
    name: "Citations",
    yaxis: "y2",
    line: { color: "#8b5cf6", width: 3 },
  };
  const dualAxisLayout = {
    margin: { l: 50, r: 50, t: 20, b: 40 },
    showlegend: true,
    legend: { orientation: "h", y: -0.2 },
    xaxis: { title: "" },
    yaxis: { title: "Publications" },
    yaxis2: { title: "Citations", overlaying: "y", side: "right" },
    height: 300,
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
  };

  return (
    <div className="space-y-6">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Welcome, {data.user?.name}</h1>
          <p className="text-slate-500 text-sm">Your research intelligence overview</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleRefreshRecommendations}
            disabled={refreshing}
            className="btn-secondary text-sm"
          >
            {refreshing ? "Refreshing…" : "🔄 Refresh Recommendations"}
          </button>
          <Link to="/recommendations" className="btn-primary">🎯 View AI Recommendations</Link>
        </div>
      </div>

      {/* KPI Cards — every value is sourced from the backend `metrics`
          block. The order matches the spec and is never hardcoded.
          Saved Patents is sourced from the SavedPatentsContext so it
          stays in sync after save/remove actions taken elsewhere. */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Publications" value={metrics.publications ?? 0} subtitle="Total" color="primary" icon="📄" />
        <StatCard title="Citations" value={metrics.citations ?? 0} subtitle="All time" color="purple" icon="📚" />
        <StatCard title="Innovation Score" value={metrics.innovation_score ?? 0} subtitle="Out of 100" color="green" icon="💡" />
        <StatCard title="Commercialization" value={metrics.commercialization_score ?? 0} subtitle="Out of 100" color="amber" icon="🚀" />
        <StatCard title="H-Index" value={metrics.h_index ?? 0} subtitle="Author metric" color="primary" icon="📈" />
        <StatCard title="I10-Index" value={metrics.i10_index ?? 0} subtitle="10+ citations" color="primary" icon="📊" />
        <StatCard title="Available Funding" value={metrics.available_funding ?? 0} subtitle="Active opportunities" color="green" icon="💰" />
        <StatCard title="Productivity" value={metrics.productivity ?? 0} subtitle="Avg cites/pub" color="purple" icon="⚡" />
        <Link
          to="/saved-patents"
          className="card hover:shadow-md transition block"
          aria-label={`View your ${savedPatentsCount} saved patents`}
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-slate-500">Saved Patents</div>
              <div className="text-3xl font-bold mt-1 text-blue-600">
                {savedPatentsCount ?? 0}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Your bookmark library →
              </div>
            </div>
            <div className="text-3xl opacity-50">⭐</div>
          </div>
        </Link>
      </div>

      {/* Innovation Radar (Chart.js) + Funding Bubble (Plotly) */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">🎯 Innovation Profile</h3>
          <Radar data={radarData} options={{ responsive: true, maintainAspectRatio: true, scales: { r: { suggestedMin: 0, suggestedMax: 100 } } }} />
        </div>
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">💰 Funding Opportunities by Domain</h3>
          {fundingByDomain.length > 0 ? (
            <Plot data={[bubbleTrace]} layout={bubbleLayout} useResizeHandler style={{ width: "100%" }} config={{ displayModeBar: false }} />
          ) : (
            <EmptyChart text="No funding data yet" />
          )}
        </div>
      </div>

      {/* Standard charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Citation Trends</h3>
          {(data.citation_trends || []).length > 0 ? (
            <Line data={citationData} options={{ responsive: true, maintainAspectRatio: true }} />
          ) : (
            <EmptyChart text="Add publications to see citation trends" />
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Domain Distribution</h3>
          {(data.domain_distribution || []).length > 0 ? (
            <Doughnut data={domainData} options={{ responsive: true, maintainAspectRatio: true }} />
          ) : (
            <EmptyChart text="No domain data yet" />
          )}
        </div>
      </div>

      {/* Plotly dual-axis chart: research growth + citations */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">📈 Research Growth vs. Citation Impact</h3>
        {(data.research_growth || []).length > 0 ? (
          <Plot data={[growthTrace, citationTrace]} layout={dualAxisLayout} useResizeHandler style={{ width: "100%" }} config={{ displayModeBar: false }} />
        ) : (
          <EmptyChart text="Add publications to see growth analytics" />
        )}
      </div>

      {/* Research growth bar */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">Publications per Year</h3>
        {(data.research_growth || []).length > 0 ? (
          <Bar data={growthData} options={{ responsive: true, maintainAspectRatio: true }} />
        ) : (
          <EmptyChart text="Add publications to see growth" />
        )}
      </div>

      {/* Trending keywords */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">Top Trending Keywords</h3>
        <div className="flex flex-wrap gap-2">
          {(data.trending_keywords || []).slice(0, 20).map((kw) => (
            <span key={kw.keyword} className="badge-primary">
              {kw.keyword} <span className="ml-1 opacity-60">({kw.count})</span>
            </span>
          ))}
          {(!data.trending_keywords || data.trending_keywords.length === 0) && (
            <p className="text-sm text-slate-500">Add publications to discover trends</p>
          )}
        </div>
      </div>

      {/* Funding overview */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">Funding Landscape</h3>
        <div className="grid sm:grid-cols-3 gap-4">
          <div className="p-4 bg-primary-50 rounded-lg">
            <div className="text-sm text-slate-600">Total Opportunities</div>
            <div className="text-2xl font-bold text-primary-700">{data.funding_overview?.total || 0}</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-sm text-slate-600">Active</div>
            <div className="text-2xl font-bold text-green-700">{data.funding_overview?.active || 0}</div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="text-sm text-slate-600">Domains Covered</div>
            <div className="text-2xl font-bold text-purple-700">{data.funding_overview?.by_domain?.length || 0}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyChart({ text }) {
  return <div className="h-48 flex items-center justify-center text-slate-400 text-sm">{text}</div>;
}
