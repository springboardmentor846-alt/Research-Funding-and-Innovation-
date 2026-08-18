import React, { useEffect, useState } from "react";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  StatCard,
  useToasts,
  ToastStack,
  downloadFile,
} from "../../components/admin/ui.jsx";

const REPORTS = [
  {
    key: "users",
    title: "User Analytics",
    description: "Demographics, roles, account status, and join trends.",
    icon: "👥",
    color: "primary",
    fields: ["total_users", "active_users", "verified_users", "by_role", "active_30d"],
  },
  {
    key: "funding",
    title: "Funding Analytics",
    description: "Opportunities, active vs expired, by type/domain/country.",
    icon: "💰",
    color: "green",
    fields: ["total_funding", "active_funding", "expired_funding", "by_type", "by_domain"],
  },
  {
    key: "publications",
    title: "Publication Analytics",
    description: "Volume, citations, top contributors, and domain coverage.",
    icon: "📄",
    color: "purple",
    fields: ["total_publications", "total_citations", "recent_additions_30d", "by_domain", "top_contributors"],
  },
  {
    key: "patents",
    title: "Patent Analytics",
    description: "Coverage, technology distribution, and citations.",
    icon: "🔬",
    color: "blue",
    fields: ["total_patents", "total_citations", "by_source", "by_technology", "by_year"],
  },
  {
    key: "ai",
    title: "AI Recommendation Analytics",
    description: "Engine health, accuracy, and quality distribution.",
    icon: "🎯",
    color: "amber",
    fields: ["total_recommendations", "unique_users", "avg_similarity_score", "by_quality"],
  },
];

function ReportPanel({ report, data, loading, error, onRetry }) {
  return (
    <div className="card">
      <div className="flex items-start gap-3 mb-4">
        <div className="text-3xl">{report.icon}</div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-800">{report.title}</h3>
          <p className="text-sm text-slate-500">{report.description}</p>
        </div>
      </div>
      {loading ? (
        <p className="text-sm text-slate-500">Loading...</p>
      ) : error ? (
        <ErrorBanner message={error} onRetry={onRetry} />
      ) : !data ? null : (
        <div className="space-y-2 text-sm">
          {report.key === "users" && (
            <>
              <Row label="Total users" value={data.total_users} />
              <Row label="Active" value={data.active_users} />
              <Row label="Verified" value={data.verified_users} />
              <Row label="Inactive" value={data.inactive_users} />
              <Row label="Active (30d)" value={data.active_30d} />
              <SubRow label="By role" items={data.by_role} />
            </>
          )}
          {report.key === "funding" && (
            <>
              <Row label="Total" value={data.total_funding} />
              <Row label="Active" value={data.active_funding} />
              <Row label="Inactive" value={data.inactive_funding} />
              <Row label="Expired" value={data.expired_funding} />
              <Row label="Added (30d)" value={data.recent_additions_30d} />
              <SubRow label="By type" items={data.by_type} itemKey="type" />
              <SubRow label="By domain" items={data.by_domain} itemKey="domain" />
              <SubRow label="By country" items={data.by_country} itemKey="country" />
            </>
          )}
          {report.key === "publications" && (
            <>
              <Row label="Total" value={data.total_publications} />
              <Row label="Citations" value={data.total_citations} />
              <Row label="Added (30d)" value={data.recent_additions_30d} />
              <SubRow label="By domain" items={data.by_domain} itemKey="domain" />
              {data.top_contributors?.length > 0 && (
                <div>
                  <div className="text-xs text-slate-500 mt-3 mb-1">Top contributors</div>
                  <ul className="space-y-1">
                    {data.top_contributors.map((c) => (
                      <li key={c.user_id} className="flex justify-between text-sm">
                        <span className="text-slate-700">{c.full_name || c.username}</span>
                        <span className="text-slate-500">{c.count} pubs</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
          {report.key === "patents" && (
            <>
              <Row label="Total" value={data.total_patents} />
              <Row label="Citations" value={data.total_citations} />
              <SubRow label="By source" items={data.by_source} itemKey="source" />
              <SubRow label="By technology" items={data.by_technology} itemKey="technology" />
              <SubRow label="By year" items={data.by_year} itemKey="year" />
            </>
          )}
          {report.key === "ai" && (
            <>
              <Row label="Total generated" value={data.total_recommendations} />
              <Row label="Unique users" value={data.unique_users} />
              <Row label="Unique funding" value={data.unique_funding} />
              <Row label="Avg similarity" value={Number(data.avg_similarity_score).toFixed(3)} />
              <Row label="Avg rule score" value={Number(data.avg_rule_score || 0).toFixed(3)} />
              <div className="text-xs text-slate-500 mt-3 mb-1">Quality distribution</div>
              <div className="flex gap-2">
                <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-xs">
                  High: {data.by_quality?.high || 0}
                </span>
                <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-xs">
                  Medium: {data.by_quality?.medium || 0}
                </span>
                <span className="px-2 py-0.5 bg-red-100 text-red-800 rounded-full text-xs">
                  Low: {data.by_quality?.low || 0}
                </span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-1">
      <span className="text-slate-600">{label}</span>
      <span className="font-semibold text-slate-800">{value ?? 0}</span>
    </div>
  );
}

function SubRow({ label, items, itemKey }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="mt-2">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className="flex flex-wrap gap-1">
        {items.slice(0, 8).map((it, i) => (
          <span key={i} className="px-2 py-0.5 bg-slate-100 rounded-full text-xs text-slate-700">
            {itemKey ? it[itemKey] : Object.keys(it)[0]} · {it.count}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function AdminReports() {
  const [reportData, setReportData] = useState({});
  const [loadingReport, setLoadingReport] = useState(null);
  const [error, setError] = useState("");
  const { toasts, pushToast, dismissToast } = useToasts();

  async function loadReport(key) {
    setLoadingReport(key);
    setError("");
    try {
      let res;
      switch (key) {
        case "users":
          res = await adminAPI.dashboardSummary();
          setReportData((d) => ({ ...d, users: res.data.users }));
          break;
        case "funding":
          res = await adminAPI.fundingStats();
          setReportData((d) => ({ ...d, funding: res.data }));
          break;
        case "publications":
          res = await adminAPI.publicationStats();
          setReportData((d) => ({ ...d, publications: res.data }));
          break;
        case "patents":
          res = await adminAPI.patentOverview();
          setReportData((d) => ({
            patents: {
              total_patents: res.data.total_patents,
              total_citations: res.data.total_citations,
              by_source: res.data.by_source,
              by_technology: res.data.by_technology,
              by_year: res.data.by_year,
            },
          }));
          break;
        case "ai":
          res = await adminAPI.recommendationStats();
          setReportData((d) => ({ ...d, ai: res.data }));
          break;
        default:
          break;
      }
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to load ${key} report`);
    } finally {
      setLoadingReport(null);
    }
  }

  function loadAll() {
    REPORTS.forEach((r) => loadReport(r.key));
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleExport(key) {
    try {
      let res, name;
      if (key === "users") { res = await adminAPI.exportUsers(); name = "users_report.csv"; }
      else if (key === "funding") { res = await adminAPI.exportFunding(); name = "funding_report.csv"; }
      else if (key === "publications") { res = await adminAPI.exportPublications(); name = "publications_report.csv"; }
      else if (key === "patents") { res = await adminAPI.exportPatents(); name = "patents_report.csv"; }
      else { return; }
      await downloadFile(res, name);
      pushToast(`${name} downloaded`, "success");
    } catch (err) {
      pushToast("Export failed", "error");
    }
  }

  const allLoaded = REPORTS.every((r) => reportData[r.key]);
  const totals = {
    users: reportData.users?.total_users,
    funding: reportData.funding?.total_funding,
    publications: reportData.publications?.total_publications,
    patents: reportData.patents?.total_patents,
    ai: reportData.ai?.total_recommendations,
  };

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Reports & Analytics</h1>
          <p className="text-slate-500 text-sm">
            Platform insights across users, funding, publications, patents, and AI
          </p>
        </div>
        <button onClick={loadAll} className="btn-secondary text-sm">🔄 Refresh All</button>
      </div>

      {!allLoaded && loadingReport ? (
        <PageLoader label="Loading analytics..." />
      ) : null}

      {error && <ErrorBanner message={error} onRetry={loadAll} />}

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <StatCard title="Users" value={totals.users} color="primary" icon="👥" />
        <StatCard title="Funding" value={totals.funding} color="green" icon="💰" />
        <StatCard title="Publications" value={totals.publications} color="purple" icon="📄" />
        <StatCard title="Patents" value={totals.patents} color="blue" icon="🔬" />
        <StatCard title="AI Recs" value={totals.ai} color="amber" icon="🎯" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {REPORTS.map((r) => (
          <div key={r.key} className="space-y-3">
            <ReportPanel
              report={r}
              data={reportData[r.key]}
              loading={loadingReport === r.key}
              error={loadingReport === r.key ? null : null}
              onRetry={() => loadReport(r.key)}
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => handleExport(r.key)}
                className="btn-secondary text-xs"
                disabled={!reportData[r.key]}
              >
                ⬇ Export CSV
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="card bg-slate-50">
        <h3 className="font-semibold text-slate-800 mb-2">PDF Reports</h3>
        <p className="text-sm text-slate-600">
          For PDF exports, use your browser's <strong>Print → Save as PDF</strong> feature
          on any analytics panel. CSV exports of all reports are available via the buttons above.
        </p>
      </div>
    </div>
  );
}
