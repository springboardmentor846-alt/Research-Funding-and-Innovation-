import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
import { Bar, Doughnut, Line } from "react-chartjs-2";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  StatCard,
  Badge,
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

const ROLE_LABELS = {
  researcher: "Researchers",
  startup_founder: "Startup Founders",
  innovation_manager: "Innovation Managers",
  admin: "Admins",
};

function relativeTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

const ACTIVITY_TONE = {
  user_signup: "primary",
  publication_added: "purple",
  funding_added: "success",
  recommendation_generated: "warning",
};

const ACTIVITY_LABEL = {
  user_signup: "New user",
  publication_added: "Publication",
  funding_added: "Funding",
  recommendation_generated: "AI recommendation",
};

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [s, a] = await Promise.all([
        adminAPI.dashboardSummary(),
        adminAPI.recentActivity(15),
      ]);
      setSummary(s.data);
      setActivity(a.data.items || []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load admin dashboard."
      );
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <PageLoader label="Loading admin dashboard..." />;
  if (error) return <ErrorBanner message={error} onRetry={load} />;
  if (!summary) return null;

  const kpis = summary.kpis || {};
  const userStats = summary.users || {};
  const fundStats = summary.funding || {};
  const pubStats = summary.publications || {};
  const recStats = summary.ai_recommendations || {};
  const patentTotal = kpis.total_patents ?? 0;

  // Charts
  const roleData = {
    labels: Object.keys(userStats.by_role || {}).map((k) => ROLE_LABELS[k] || k),
    datasets: [
      {
        data: Object.values(userStats.by_role || {}),
        backgroundColor: ["#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"],
        borderWidth: 0,
      },
    ],
  };

  const fundingByType = {
    labels: (fundStats.by_type || []).map((b) => b.type || "Other"),
    datasets: [
      {
        label: "Funding by type",
        data: (fundStats.by_type || []).map((b) => b.count),
        backgroundColor: "#3b82f6",
        borderRadius: 4,
      },
    ],
  };

  const pubsByDomain = {
    labels: (pubStats.by_domain || []).slice(0, 8).map((b) => b.domain),
    datasets: [
      {
        label: "Publications",
        data: (pubStats.by_domain || []).slice(0, 8).map((b) => b.count),
        backgroundColor: "#8b5cf6",
        borderRadius: 4,
      },
    ],
  };

  const sysData = {
    labels: ["Funding", "Publications", "Patents", "AI Recs"],
    datasets: [
      {
        label: "Platform totals",
        data: [
          kpis.total_funding || 0,
          kpis.total_publications || 0,
          kpis.total_patents || 0,
          kpis.total_recommendations || 0,
        ],
        backgroundColor: ["#10b981", "#8b5cf6", "#3b82f6", "#f59e0b"],
        borderRadius: 4,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Admin Dashboard</h1>
          <p className="text-slate-500 text-sm">
            Platform-wide overview and management insights
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/admin/users" className="btn-secondary text-sm">👥 Manage Users</Link>
          <Link to="/admin/funding-intel" className="btn-primary text-sm">🛰 Funding Intel</Link>
        </div>
      </div>

      {/* KPI Tiles */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Total Users"
          value={kpis.total_users}
          subtitle={`${userStats.active_users || 0} active`}
          color="primary"
          icon="👥"
        />
        <StatCard
          title="Funding"
          value={kpis.total_funding}
          subtitle={`${fundStats.active_funding || 0} active`}
          color="green"
          icon="💰"
        />
        <StatCard
          title="Publications"
          value={kpis.total_publications}
          subtitle={`${pubStats.recent_additions_30d || 0} new (30d)`}
          color="purple"
          icon="📄"
        />
        <StatCard
          title="Patents"
          value={patentTotal}
          subtitle="Tracked across registries"
          color="blue"
          icon="🔬"
        />
        <StatCard
          title="AI Recommendations"
          value={kpis.total_recommendations}
          subtitle={`avg ${recStats.avg_similarity_score || 0} score`}
          color="amber"
          icon="🎯"
        />
        <StatCard
          title="Active (30d)"
          value={kpis.active_30d}
          subtitle="Recent logins"
          color="red"
          icon="⚡"
        />
      </div>

      {/* System Overview */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">System Overview</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <div className="p-3 rounded-lg bg-blue-50">
            <div className="text-xs text-slate-500">Verified Users</div>
            <div className="text-xl font-bold text-blue-700">
              {userStats.verified_users || 0}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-amber-50">
            <div className="text-xs text-slate-500">Inactive Users</div>
            <div className="text-xl font-bold text-amber-700">
              {userStats.inactive_users || 0}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-green-50">
            <div className="text-xs text-slate-500">Total Citations</div>
            <div className="text-xl font-bold text-green-700">
              {pubStats.total_citations || 0}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-purple-50">
            <div className="text-xs text-slate-500">Expired Funding</div>
            <div className="text-xl font-bold text-purple-700">
              {fundStats.expired_funding || 0}
            </div>
          </div>
        </div>
        <div className="h-56">
          <Bar
            data={sysData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
            }}
          />
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Users by Role</h3>
          <div className="h-64 flex items-center justify-center">
            {Object.keys(userStats.by_role || {}).length ? (
              <Doughnut
                data={roleData}
                options={{ responsive: true, maintainAspectRatio: false }}
              />
            ) : (
              <p className="text-sm text-slate-400">No users yet</p>
            )}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Funding by Type</h3>
          <div className="h-64">
            {(fundStats.by_type || []).length ? (
              <Bar
                data={fundingByType}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                }}
              />
            ) : (
              <p className="text-sm text-slate-400">No funding yet</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Top Publication Domains</h3>
          <div className="h-64">
            {(pubStats.by_domain || []).length ? (
              <Bar
                data={pubsByDomain}
                options={{
                  indexAxis: "y",
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                }}
              />
            ) : (
              <p className="text-sm text-slate-400">No publications yet</p>
            )}
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800">Recent Activity</h3>
            <span className="text-xs text-slate-400">Last {activity.length} events</span>
          </div>
          {activity.length === 0 ? (
            <p className="text-sm text-slate-400">No activity yet</p>
          ) : (
            <ul className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
              {activity.map((a, i) => (
                <li key={i} className="py-2 flex items-start gap-3 text-sm">
                  <Badge tone={ACTIVITY_TONE[a.type] || "slate"}>
                    {ACTIVITY_LABEL[a.type] || a.type}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="text-slate-700 truncate">{a.description}</div>
                    <div className="text-xs text-slate-400">
                      {relativeTime(a.at)} · {a.actor}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
